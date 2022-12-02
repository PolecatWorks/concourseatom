# concourseatom Copyright (C) 2022 Ben Greene
"""Data models for working with concourse data obejects
"""

from __future__ import annotations
from abc import ABC, abstractmethod  # This enables forward reference of types
from typing import Any, Dict, Optional, List, Tuple, Union

from pydantic import Field, validator
from pydantic_yaml import YamlModel


def get_uniquename(name: str, namelist: List[str]) -> str:
    """get a unique name to add to the list based on its original name and
    incrementing the counter until we hit a unique entry"""

    index_num = 0
    b_alt_name = f"{name}-{index_num:0>3}"
    while b_alt_name in namelist:
        index_num += 1
        b_alt_name = f"{name}-{index_num:0>3}"

    return b_alt_name


def get_random_ingredients(kind=None):
    """
    >>> 1+1
    2
    >>> 1/0 # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
      ...
    ZeroDivisionError: integer division or modulo by zero
    """
    return ["shells", "gorgonzola", "parsley"]


class StepABC(ABC):
    """ABC for Step class
    Step class represents objects of type step used by concourse plans
    """

    def deep_merge(self, other: StepABC):
        if self != other:
            raise Exception(f"deep_merge items MUST be identical: {self} != {other}")

    @abstractmethod
    def handles(self) -> List[Tuple[str, str]]:
        """
        Recursively get the handles used by the job AND their resource if there
        is one.

        Returns:
            List[Tuple[str, str]]: List of handle, resource
        """
        pass


class RewritesABC(ABC):
    @abstractmethod
    def resource_rewrite(self, rewrites: Dict[str, str]) -> StepABC:
        pass

    def exactEq(self, other: RewritesABC) -> bool:
        return self.name == other.name and self == other

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def uniques_and_rewrites(
        cls, aList: List[RewritesABC], bList: List[RewritesABC], deep: bool = False
    ) -> Tuple[List[RewritesABC], Dict[str, str]]:
        """
        aList gets priority and copied verbatim
        If item already exists in aList then create rewrite from its name in bList
        If name already exists in aList then identify a rename and map that rename

        capture list of appended items to be added to aList

        return the final list AND a dict of resource_rewrites and handle_rewrites
        """

        ret_list: List[RewritesABC] = aList.copy()
        resource_rewrite_map: Dict[str, str] = {}

        for item in bList:
            if item in ret_list:  # Item already exists so map it
                resource_rewrite_map[item.name] = next(
                    obj.name for obj in ret_list if obj == item
                )
            elif any(
                resource.name == item.name for resource in ret_list
            ):  # Name already used for different item so rename it and then add
                # If using deep mode then work out the recursive deep merge

                if deep:
                    # Note deep is only valid for Job (not Resource or Resource_type)
                    print(f"Doing a deep merge and working on item called: {item.name}")

                    # get the item we plan to deep merge in
                    target_item = next(
                        resource for resource in ret_list if resource.name == item.name
                    )
                    print(f"Doing deep update to: {type(target_item)} {target_item}")

                    target_handles = target_item.handles()
                    handles = item.handles()

                    # ToDo: dedup here

                    handle_rewrites: Dict[str, str] = {}
                    handle_list = target_handles.copy()

                    for handle in handles:
                        if handle in handle_list:
                            # if handle in target and same resource then rewrite to same
                            # name NOT add to list
                            handle_rewrites[handle[0]] = handle[0]
                        elif handle[0] in (
                            target_handle
                            for target_handle, target_resource in handle_list
                        ):
                            # if handle in target BUT different resource the create
                            # rewrite of handle
                            alt_name = get_uniquename(
                                handle[0],
                                (
                                    target_handle
                                    for target_handle, target_resource in handle_list
                                ),
                            )
                            handle_rewrites[handle[0]] = alt_name
                            handle_list.append((alt_name, handle[1]))
                        else:
                            # else add entry and rewrite to itself
                            handle_rewrites[handle[0]] = handle[0]
                            handle_list.append(handle)

                    new_target = target_item.deep_merge(item)
                    print(new_target)
                    # Do not update ret_list via append as items are deep_merged in
                else:

                    print("Doing shallow copy")
                    # Get the list of all names in output objects
                    namelist = [resource.name for resource in ret_list]

                    alt_name = get_uniquename(item.name, namelist)

                    # Update the new name with the proposed rewrite name
                    resource_rewrite_map[item.name] = alt_name

                    ret_list.append(item.copy(deep=True, update={"name": alt_name}))
            else:  # Item is unique so add it
                resource_rewrite_map[item.name] = item.name
                ret_list.append(item.copy(deep=True))

        return ret_list, resource_rewrite_map

    @classmethod
    def rewrites(
        cls,
        in_list: List[RewritesABC],
        resource_rewrites: Dict[str, str],
    ) -> List[RewritesABC]:
        """Apply rewrite pattern to type parameter"""
        return [resource.resource_rewrite(resource_rewrites) for resource in in_list]


class ResourceType(YamlModel, RewritesABC):
    name: str
    type: str
    source: Dict[str, Any] = Field(default_factory=dict)
    privileged: bool = False
    params: Dict[str, Any] = Field(default_factory=dict)
    check_every: str = "1m"
    tags: list[str] = Field(default_factory=list)
    defaults: Dict[str, Any] = Field(default_factory=dict)

    def __eq__(self, other: ResourceType) -> bool:
        return (
            self.type == other.type
            and self.source == other.source
            and self.privileged == other.privileged
            and self.params == other.params
            and self.check_every == other.check_every
            and self.tags == other.tags
            and self.defaults == other.defaults
        )

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> ResourceType:
        return self.copy(deep=True, update={"type": resource_rewrites[self.type]})

    def __lt__(self, other):
        return self.type < other.type


class ResourceUnnamed(YamlModel, RewritesABC):
    type: str
    source: Dict[str, Any]
    old_name: Optional[str] = None
    icon: Optional[str] = None
    version: Optional[str] = None
    check_every: str = "1m"
    check_timeout: str = "1h"
    expose_build_created_by: bool = False
    tags: list[str] = Field(default_factory=list)
    public: bool = False
    webhook_token: Optional[str] = None

    def __eq__(self, other: Resource) -> bool:
        return (
            self.type == other.type
            and self.source == other.source
            and self.old_name == other.old_name
            and self.icon == other.icon
            and self.version == other.version
            and self.check_every == other.check_every
            and self.check_timeout == other.check_timeout
            and self.expose_build_created_by == other.expose_build_created_by
            and self.tags == other.tags
            and self.public == other.public
            and self.webhook_token == other.webhook_token
        )

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Resource:
        return self.copy(deep=True, update={"type": resource_rewrites[self.type]})

    def __lt__(self, other):
        return self.type < other.type


class Resource(ResourceUnnamed):
    name: str
    # ToDo: is this valid or should this be dropped and jsut use ResourceUnnamed
    # directly


class Command(YamlModel):
    """Command definition for task

    :param path: Path to executable
    :param args: args to provide to cmd
    :param dir: dir from where to run from PWD
    :param user: User for executing cmd
    """

    path: str
    args: List[str] = Field(default_factory=list)
    dir: Optional[str] = None
    user: Optional[str] = None


class Input(YamlModel):
    name: str
    path: Optional[str] = None
    optional: bool = False

    def __post_init__(self):
        if not self.path:
            self.path = self.name


class Output(YamlModel):
    name: str
    path: Optional[str] = None

    def __post_init__(self):
        if not self.path:
            self.path = self.name


class Cache(YamlModel):
    path: str


class Container_limits(YamlModel):
    cpu: int
    memory: int


class TaskConfig(YamlModel):
    platform: str
    run: Command
    image_resource: Optional[ResourceUnnamed] = None
    inputs: List[Input] = Field(default_factory=list)
    outputs: List[Output] = Field(default_factory=list)
    caches: List[Cache] = Field(default_factory=list)
    params: Dict[str, str] = Field(default_factory=dict)
    rootfs_uri: Optional[str] = None
    container_limits: Optional[Container_limits] = None


class Task(YamlModel, StepABC, RewritesABC):
    """Concourse Task class

    :param task: Name of the task
    """

    task: str
    config: Optional[TaskConfig] = None
    file: Optional[str] = None
    image: Optional[str] = None
    priviledged: bool = False
    vars: Dict[str, str] = Field(default_factory=dict)
    container_limits: Optional[Container_limits] = None
    params: Dict[str, str] = Field(default_factory=dict)
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    output_mapping: Dict[str, str] = Field(default_factory=dict)

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Get:
        if not self.config:
            raise Exception(f"Task needs config for {self}")
        if self.file:
            raise Exception(f"No support for file in {self}")

        return self.copy(
            deep=True,
        )

        # return self.copy(
        #     deep=True,
        #     update={
        #         "input_mapping": {
        #             input.name: resource_rewrites[input.name]
        #             for input in self.config.inputs
        #         },
        #         "output_mapping": {
        #             output.name: resource_rewrites[output.name]
        #             for output in self.config.outputs
        #         },
        #     },
        # )

    def handles(self) -> List[Tuple[str, str]]:
        retval: List[Tuple[str, str]] = []

        for handle in self.config.inputs:
            retval.append((handle.name, None))
        for handle in self.config.outputs:
            retval.append((handle.name, None))

        # ToDo: Consider input_mapping and output_mapping also

        return retval


class Get(YamlModel, StepABC, RewritesABC):
    get: str
    resource: Optional[str] = None
    passed: List[str] = Field(default_factory=list)
    params: Optional[Any] = None
    trigger: bool = False
    version: str = "latest"

    def effective_resource(self):
        return self.resource if self.resource else self.get

    def __post_init__(self):
        if not self.resource:
            self.resource = self.get

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Get:
        return self.copy(
            deep=True, update={"resource": resource_rewrites[self.effective_resource()]}
        )

    def deep_merge(self, other: RewritesABC):
        if self != other:
            raise Exception("Default deep_merge process just checks identicial")

    def handles(self) -> List[Tuple[str, str]]:
        return [(self.get, self.resource if self.resource else self.get)]


class Put(YamlModel, StepABC, RewritesABC):
    put: str
    resource: Optional[str] = None
    inputs: str = "all"
    params: Optional[Any] = None
    get_params: Optional[Any] = None

    def __post_init__(self):
        if not self.resource:
            self.resource = self.put

    def effective_resource(self):
        return self.resource if self.resource else self.put

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Put:
        return self.copy(
            deep=True, update={"resource": resource_rewrites[self.effective_resource()]}
        )

    def handles(self) -> List[Tuple[str, str]]:
        return [(self.put, self.resource if self.resource else self.put)]


class Do(YamlModel, StepABC, RewritesABC):
    do: List[Step]

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Do:
        return self.copy(
            deep=True,
            update={
                "do": [step.resource_rewrite(resource_rewrites) for step in self.do]
            },
        )

    def handles(self) -> List[Tuple[str, str]]:

        return [handle for step in self.do for handle in step.handles()]


class In_parallel(YamlModel, StepABC, RewritesABC):
    class Config(YamlModel):
        steps: List[Step] = Field(default_factory=list)
        limit: Optional[int] = None
        fail_fast: bool = False

    in_parallel: Union[In_parallel.Config, List[Step]]
    # ToDo: Consider to provide in_parallel as a Union[List[Step], In_parallel.Config]

    @validator("in_parallel")
    def cooerce_in_parallel_to_verbose(cls, value):
        if not isinstance(value, In_parallel.Config):
            return In_parallel.Config(steps=value)
        return value

    # def __post_init_post_parse__(self, in_parallel):
    #     # If provided in shortened form then force to verbose form
    #     if not isinstance(in_parallel, In_parallel.Config):
    #         self.in_parallel = In_parallel.Config(steps=self.in_parallel)
    #     bark

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> In_parallel:
        return self.copy(
            deep=True,
            update={
                "in_parallel": self.in_parallel.copy(
                    deep=True,
                    update={
                        "steps": [
                            step.resource_rewrite(resource_rewrites)
                            for step in self.in_parallel.steps
                        ]
                    },
                ),
            },
        )

    def handles(self) -> List[Tuple[str, str]]:
        return [handle for step in self.in_parallel.steps for handle in step.handles()]

    def deep_merge(self, other: In_parallel):
        # For every item in the add it if it does not already exist
        for newitem in other.in_parallel.steps:
            if newitem not in self.in_parallel.steps:
                self.in_parallel.steps.append(newitem)


Step = Union[Get, Put, Task, In_parallel, Do]

Do.update_forward_refs()
In_parallel.update_forward_refs()
In_parallel.Config.update_forward_refs()


class LogRetentionPolicy(YamlModel):
    """Log Retention for concoure job

    :param days: Number of days to keep logs for
    :type task: int
    :param builds: Number of builds to retain
    :type builds: int
    :param minimum_succeeded_builds: Minimum number of successful builds to retain
    :type minimum_succeeded_builds: int
    """

    days: int
    builds: int
    minimum_succeeded_builds: int


class Job(YamlModel, RewritesABC):
    name: str
    plan: List[Step]
    old_name: Optional[str] = None
    serial: bool = False
    serial_groups: List[str] = Field(default_factory=list)
    max_in_flight: Optional[int] = None
    build_log_retention: Optional[LogRetentionPolicy] = None
    public: bool = False
    disable_manual_trigger: bool = False
    interruptible: bool = False
    on_success: Optional[Step] = None
    on_failure: Optional[Step] = None
    on_error: Optional[Step] = None
    on_abort: Optional[Step] = None
    ensure: Optional[Step] = None

    def __eq__(self, other: Job) -> bool:
        return (
            self.plan == other.plan
            and self.old_name == other.old_name
            and self.serial == other.serial
            and self.serial_groups == other.serial_groups
            and self.max_in_flight == other.max_in_flight
            and self.build_log_retention == other.build_log_retention
            and self.public == other.public
            and self.disable_manual_trigger == other.disable_manual_trigger
            and self.interruptible == other.interruptible
        )

    def resource_rewrite(
        self,
        resource_rewrites: Dict[str, str],
    ) -> Job:
        return self.copy(
            deep=True,
            update={
                "plan": [
                    step.resource_rewrite(resource_rewrites) for step in self.plan
                ],
                "on_success": self.on_success.resource_rewrite(resource_rewrites)
                if self.on_success
                else None,
                "on_failure": self.on_failure.resource_rewrite(resource_rewrites)
                if self.on_failure
                else None,
                "on_error": self.on_error.resource_rewrite(resource_rewrites)
                if self.on_error
                else None,
                "on_abort": self.on_abort.resource_rewrite(resource_rewrites)
                if self.on_abort
                else None,
                "ensure": self.ensure.resource_rewrite(resource_rewrites)
                if self.ensure
                else None,
            },
        )

    def handle_rewrite(
        self,
        handle_rewrites: Dict[str, str],
    ) -> Job:
        print("WORK TO DO HERE")
        return self.copy(
            deep=True,
        )

    def deep_merge(self, other: Job):

        # Check rules before we attempt the deep_merge
        if (
            self.on_abort != other.on_abort
            or self.on_error != other.on_error
            or self.on_failure != other.on_failure
            or self.on_success != other.on_success
        ):
            raise Exception("Cannot merge job if different on_ tasks")

        # if we have anything but in_parallel then these must be identical
        if len(self.plan) != len(other.plan):
            raise Exception("deep_merge only when plans are same length")

        for selfPlan, otherPlan in zip(self.plan, other.plan):
            print(f"DEEP_MERGING: {selfPlan} {otherPlan}")
            selfPlan.deep_merge(otherPlan)

    def handles(self) -> List[Tuple[str, str]]:
        # list_list = [step.handles() for step in self.plan]
        return [handle for step in self.plan for handle in step.handles()]

    @classmethod
    def resource_rewrites(
        cls,
        in_list: List[RewritesABC],
        resource_rewrites: Dict[str, str],
    ) -> List[RewritesABC]:
        """Apply resource_rewrite pattern to objects"""
        return [resource.resource_rewrite(resource_rewrites) for resource in in_list]

    @classmethod
    def handle_rewrites(
        cls,
        in_list: List[Job],
        handle_rewrites: Dict[str, Dict[str, str]],
    ) -> List[Job]:
        """Apply handle_rewrite pattern to objects"""
        return [job.handle_rewrite(handle_rewrites[job.name]) for job in in_list]

    @classmethod
    def handle_uniques_and_rewrites(
        cls, jobs_left: List[Job], jobs_right: List[Job]
    ) -> Dict[str, Dict[str, str]]:
        """
        Returns the name of the job and the rewrites for then handles in that job
        rewrites are direct copies if no collisions else collision rules apply
        (re-use or copy)
        """
        print(f"handle_rewrites for {jobs_left} and {jobs_right}")
        if jobs_right:
            print("TODO STOP HERE")
        return {}


class Pipeline(YamlModel):
    """Definition of a concourse plan"""

    resource_types: list[ResourceType] = Field(default_factory=list)
    resources: list[Resource] = Field(default_factory=list)
    jobs: List[Job] = Field(default_factory=list)

    def __eq__(self, other: Pipeline) -> bool:
        return (
            sorted(self.resource_types) == sorted(other.resource_types)
            and sorted(self.resources) == sorted(other.resources)
            and sorted(self.jobs) == sorted(other.jobs)
        )

    def exactEq(self, other: Pipeline) -> bool:
        if self != other:
            return False

        return (
            all(
                left.exactEq(right)
                for left, right in zip(
                    sorted(self.resource_types), sorted(other.resource_types)
                )
            )
            and all(
                left.exactEq(right)
                for left, right in zip(sorted(self.resources), sorted(other.resources))
            )
            and all(
                left.exactEq(right)
                for left, right in zip(sorted(self.jobs), sorted(other.jobs))
            )
        )

    def __post_init__(self):
        self.resource_types.sort()
        self.resources.sort()
        self.jobs.sort()

    def validate(self) -> bool:
        """Check if the Pipeline is valid

        Rules:

        - Check that all resource types referred to from resources are defined
        - Check that all resources used by Get and Put are defined in Resources
            (TODO: Add check for resources)
        :return: all rules are passed
        """
        resource_type_names = [rt.name for rt in self.resource_types]

        return all(
            (resource.type in resource_type_names) for resource in self.resources
        )

    @classmethod
    def merge(
        cls, pipeline_left: Pipeline, pipeline_right: Pipeline, deep: bool = False
    ) -> Pipeline:
        """Merge two Concourse Plans

        Merge will take two Things and create a merge of them.
        It will resolve shared resources and map into a single name.
        It will resolve different resources with same name into discrete resourcess.
        The secondary plan be modified in naming, but not in function during the merge
        to achieve minimal :class:`Resource` s and :class:`ResourceType` s.

        :param aThing: Base concourse plan to add second plan to.
        This will be unchanged through merge process
        :param bThing: Secondary plan.
        :param deep: Deep mode attempts to merge jobs based on name and cooerce merges
            serial and parallel objects

        :Return:
            Merged output from combination of both inputs with minimised
            :class:`Resource` s and :class:`ResourceType` s
        """

        if not pipeline_left.validate():
            raise Exception(f"pipeline_left is not valid: {pipeline_left}")

        if not pipeline_right.validate():
            raise Exception(f"pipeline_right is not valid: {pipeline_right}")

        # set of resource_types from merge and rewrites of resources to achieve this
        (
            resource_types,
            resource_types_right_rewrites,
        ) = ResourceType.uniques_and_rewrites(
            pipeline_left.resource_types, pipeline_right.resource_types
        )

        # resource_types updated for resources from RHS
        resources_right_rewritten = Resource.rewrites(
            pipeline_right.resources, resource_types_right_rewrites
        )

        # Unique resources and rewrites to achieve this
        resources, resources_right_rewrites = Resource.uniques_and_rewrites(
            pipeline_left.resources, resources_right_rewritten
        )

        # NOT WHAT NEXT
        # 1. Update RHS with all resource rewrites ????
        #      if RHS is get/put then can keep handle as is and modify the resource it
        #      points to SO all handles stay same.
        #      No need to modify ANY handles (ie gets/puts are only interfaces to
        #      resources so these solve all updates of resources)
        # 2. If we also do deep merge then we can (inside parallel steps) add more
        #      handles and result in handle collision.
        #      To solve this we identify the uniques and renames of handles through
        #      merges (ONLY when job names match) and then we generate
        #      the set of handle uniques and renames needed for RHS.

        jobs_right_rewritten = Job.resource_rewrites(
            pipeline_right.jobs, resources_right_rewrites
        )

        # # Evaluate the rewrites necessary for clashes if we run a deep merge
        # jobs_right_handles_rewrites  = Job.handle_uniques_and_rewrites(
        #     pipeline_left.jobs, jobs_right_rewritten
        # )

        # jobs_right_handles_rewritten = Job.handle_rewrites(
        #     jobs_right_rewritten, jobs_right_handles_rewrites
        # )

        # for each job in rhs consider to add it based on being net new OR with handle
        # rewrites internal to it (handle rewrites are only scoped to the job at hand)

        jobs, jobs_right_rewrites = Job.uniques_and_rewrites(
            pipeline_left.jobs, jobs_right_rewritten, deep
        )

        return Pipeline(resource_types=resource_types, resources=resources, jobs=jobs)
