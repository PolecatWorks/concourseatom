# concourseatom Copyright (C) 2022 Ben Greene
"""Data models for working with concourse data obejects
"""

from __future__ import annotations
from abc import ABC, abstractmethod  # This enables forward reference of types
from typing import Any, Dict, Optional, List, Tuple, Union

from pydantic import Field
from pydantic_yaml import YamlModel


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
    @abstractmethod
    def rewrite(self, rewrites: Dict[str, str]) -> StepABC:
        pass

    def deep_merge(self, other: Rewrites):
        if self != other:
            raise Exception(f"deep_merge items MUST be identical: {self} != {other}")


class Rewrites(StepABC):
    def exactEq(self, other: Rewrites) -> bool:
        return self.name == other.name and self == other

    def __lt__(self, other):
        return self.name < other.name

    @classmethod
    def uniques_and_rewrites(
        cls, aList: List[Rewrites], bList: List[Rewrites], deep: bool = False
    ) -> Tuple[List[Rewrites], Dict[str, str]]:
        """
        aList gets priority and copied verbatim
        If item already exists in aList then create rewrite from its name in bList
        If name already exists in aList then identify a rename and map that rename

        capture list of appended items to be added to aList

        return the final list AND a dict of rewrites
        """

        ret_list: List[Rewrites] = aList.copy()
        rewrite_map: Dict[str, str] = {}

        for item in bList:
            if item in ret_list:  # Item already exists so map it
                rewrite_map[item.name] = next(
                    obj.name for obj in ret_list if obj == item
                )
            elif any(
                resource.name == item.name for resource in ret_list
            ):  # Name already used for different item so rename it and then add
                # If using deep mode then work out the recursive deep merge

                if deep:
                    # Note deep is only valid for Job (not Resource or Resource_type)
                    print(f"Doing a deep merge and working on item called: {item.name}")
                    target_item = next(
                        resource for resource in ret_list if resource.name == item.name
                    )
                    print(f"Doing deep update to: {type(target_item)} {target_item}")

                    target_item.deep_merge(item)
                    # Do not update ret_list via append as items are deep_merged in
                else:

                    print("Doing shallow copy")
                    # Get the list of all names in output objects
                    namelist = [resource.name for resource in ret_list]

                    # Run through a sequence of numbers to find a number that makes a
                    # unique entry on the output names
                    index_num = 0
                    b_alt_name = f"{item.name}-{index_num:0>3}"
                    while b_alt_name in namelist:
                        index_num += 1
                        b_alt_name = f"{item.name}-{index_num:0>3}"

                    # Update the new name with the proposed rewrite name
                    rewrite_map[item.name] = b_alt_name

                    ret_list.append(item.copy(deep=True, update={"name": b_alt_name}))
            else:  # Item is unique so add it
                rewrite_map[item.name] = item.name
                ret_list.append(item.copy(deep=True))

        return ret_list, rewrite_map

    @classmethod
    def rewrites(
        cls, in_list: List[Rewrites], rewrites: Dict[str, str]
    ) -> List[Rewrites]:
        """Apply rewrite pattern to type parameter"""
        return [resource.rewrite(rewrites) for resource in in_list]


class ResourceType(YamlModel, Rewrites):
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

    def rewrite(self, rewrites: Dict[str, str]) -> ResourceType:
        return self.copy(deep=True, update={"type": rewrites[self.type]})

    def __lt__(self, other):
        return self.type < other.type


class Resource(YamlModel, Rewrites):
    name: str
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

    def rewrite(self, rewrites: Dict[str, str]) -> Resource:
        return self.copy(deep=True, update={"type": rewrites[self.type]})

    def __lt__(self, other):
        return self.type < other.type


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
    image_resource: Optional[Resource] = None
    inputs: List[Input] = Field(default_factory=list)
    outputs: List[Output] = Field(default_factory=list)
    caches: List[Cache] = Field(default_factory=list)
    params: Dict[str, str] = Field(default_factory=dict)
    rootfs_uri: Optional[str] = None
    container_limits: Optional[Container_limits] = None


class Task(YamlModel, StepABC):
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

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        if not self.config:
            raise Exception(f"Task needs config for {self}")
        if self.file:
            raise Exception(f"No support for file in {self}")

        return self.copy(
            deep=True,
            update={
                "input_mapping": {
                    input.name: rewrites[input.name] for input in self.config.inputs
                },
                "output_mapping": {
                    output.name: rewrites[output.name] for output in self.config.outputs
                },
            },
        )


class Get(YamlModel, StepABC):
    get: str
    resource: Optional[str] = None
    passed: List[str] = Field(default_factory=list)
    params: Optional[Any] = None
    trigger: bool = False
    version: str = "latest"

    def __post_init__(self):
        if not self.resource:
            self.resource = self.get

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        return self.copy(deep=True, update={"get": rewrites[self.get]})

    def deep_merge(self, other: Rewrites):
        if self != other:
            raise Exception("Default deep_merge process just checks identicial")


class Put(YamlModel, StepABC):
    put: str
    resource: Optional[str] = None
    inputs: str = "all"
    params: Optional[Any] = None
    get_params: Optional[Any] = None

    def __post_init__(self):
        if not self.resource:
            self.resource = self.put

    def rewrite(self, rewrites: Dict[str, str]) -> Put:
        return self.copy(deep=True, update={"put": rewrites[self.put]})


class Do(YamlModel, StepABC):
    do: List[Step]

    def rewrite(self, rewrites: Dict[str, str]) -> Do:
        return self.copy(
            deep=True, update={"do": [step.rewrite(rewrites) for step in self.do]}
        )


class In_parallel(YamlModel, StepABC):
    steps: List[Step] = Field(default_factory=list)
    limit: Optional[int] = None
    fail_fast: bool = False

    def rewrite(self, rewrites: Dict[str, str]) -> In_parallel:
        return self.copy(
            deep=True, update={"steps": [step.rewrite(rewrites) for step in self.steps]}
        )

    def deep_merge(self, other: In_parallel):
        # For every item in the add it if it does not already exist
        for newitem in other.steps:
            if newitem not in self.steps:
                self.steps.append(newitem)


Step = Union[Get, Put, Task, In_parallel, Do]

Do.update_forward_refs()
In_parallel.update_forward_refs()


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


class Job(YamlModel, Rewrites):
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

    def rewrite(self, rewrites: Dict[str, str]) -> Job:
        return self.copy(
            deep=True,
            update={
                "plan": [step.rewrite(rewrites) for step in self.plan],
                "on_success": self.on_success.rewrite(rewrites)
                if self.on_success
                else None,
                "on_failure": self.on_failure.rewrite(rewrites)
                if self.on_failure
                else None,
                "on_error": self.on_error.rewrite(rewrites) if self.on_error else None,
                "on_abort": self.on_abort.rewrite(rewrites) if self.on_abort else None,
                "ensure": self.ensure.rewrite(rewrites) if self.ensure else None,
            },
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

        # iamhere


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
        to achinve minimal :class:`Resource` s and :class:`ResourceType` s.

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

        resource_types, resource_types_rewrites = ResourceType.uniques_and_rewrites(
            pipeline_left.resource_types, pipeline_right.resource_types
        )

        bThing_resource_renames = Resource.rewrites(
            pipeline_right.resources, resource_types_rewrites
        )

        resources, resource_rewrites = Resource.uniques_and_rewrites(
            pipeline_left.resources, bThing_resource_renames
        )

        bThing_jobs = Job.rewrites(pipeline_right.jobs, resource_rewrites)

        jobs, job_rewrites = Job.uniques_and_rewrites(
            pipeline_left.jobs, bThing_jobs, deep
        )

        return Pipeline(resource_types=resource_types, resources=resources, jobs=jobs)
