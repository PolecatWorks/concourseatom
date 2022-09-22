"""Data models for working with concourse data obejects
"""

from __future__ import annotations
from abc import ABC, abstractmethod  # This enables forward reference of types
import dataclasses
from typing import Any, Dict, Optional, List, Tuple, Union
from ruamel.yaml import yaml_object, YAML

from dataclasses import dataclass, field


yaml = YAML()


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


class SetstateInitMixin:
    """Inject setstate function to class via a mixin"""

    def __setstate__(self, state):
        """Call init here so that yaml.load correctly initialises the objects.
        This can be a performance penalty"""
        self.__init__(**state)


@yaml_object(yaml)
@dataclass(order=True)
class ResourceType(SetstateInitMixin):
    name: str
    type: str
    source: Dict[str, Any] = field(default_factory=dict)
    privileged: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    check_every: str = "1m"
    tags: list[str] = field(default_factory=list)
    defaults: Dict[str, Any] = field(default_factory=dict)

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

    def exactEq(self, other: ResourceType) -> bool:
        return self.name == other.name and self == other

    @classmethod
    def uniques_and_rewrites(
        cls, aList: List[ResourceType], bList: List[ResourceType]
    ) -> Tuple[List[ResourceType], Dict[str, str]]:
        """
        aList gets priority and copied verbatim
        If item already exists in aList then create rewrite for that
        If name already exists in aList then create rewrite for that
        capture list of appended items to be added to aList

        return the final list
        """

        ret_list: List[ResourceType] = aList.copy()
        appendMap: Dict[str, str] = {}

        for item in bList:
            if item in ret_list:  # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [
                resource for resource in ret_list if resource.name == item.name
            ]:  # Name already used for different item so rename it and then add
                b_name_alt = "fff"
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else:  # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap


@yaml_object(yaml)
@dataclass(order=True)
class Resource(SetstateInitMixin):
    name: str
    type: str
    source: Dict[str, Any]
    old_name: Optional[str] = None
    icon: Optional[str] = None
    version: Optional[str] = None
    check_every: str = "1m"
    check_timeout: str = "1h"
    expose_build_created_by: bool = False
    tags: list[str] = field(default_factory=list)
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

    def exactEq(self, other: Resource) -> bool:
        return self.name == other.name and self == other

    @classmethod
    def uniques_and_rewrites(
        cls, aList: List[Resource], bList: List[Resource]
    ) -> Tuple[List[Resource], Dict[str, str]]:

        ret_list: List[Resource] = aList.copy()
        appendMap: Dict[str, str] = {}

        for item in bList:
            if item in ret_list:  # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [
                resource for resource in ret_list if resource.name == item.name
            ]:  # Name already used for different item so rename it and then add
                unique_num = 0
                while [
                    resource
                    for resource in ret_list
                    if resource.name == f"{item.name}-{unique_num}"
                ]:
                    unique_num += 1

                b_name_alt = f"{item.name}-{unique_num}"
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else:  # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap

    @classmethod
    def rewrite(
        cls, in_list: List[Resource], rewrites: Dict[str, str]
    ) -> List[Resource]:

        return [
            dataclasses.replace(resource, type=rewrites[resource.type])
            for resource in in_list
        ]


@yaml_object(yaml)
@dataclass
class Command(SetstateInitMixin):
    """Command definition for task

    :param path: Path to executable
    :param args: args to provide to cmd
    :param dir: dir from where to run from PWD
    :param user: User for executing cmd
    """

    path: str
    args: List[str] = field(default_factory=list)
    dir: Optional[str] = None
    user: Optional[str] = None


@yaml_object(yaml)
@dataclass
class Input(SetstateInitMixin):
    name: str
    path: Optional[str] = None
    optional: bool = False

    def __post_init__(self):
        if not self.path:
            self.path = self.name


@yaml_object(yaml)
@dataclass
class Output(SetstateInitMixin):
    name: str
    path: Optional[str] = None

    def __post_init__(self):
        if not self.path:
            self.path = self.name


@yaml_object(yaml)
@dataclass
class Cache(SetstateInitMixin):
    path: str


@yaml_object(yaml)
@dataclass
class Container_limits(SetstateInitMixin):
    cpu: int
    memory: int


@yaml_object(yaml)
@dataclass
class TaskConfig(SetstateInitMixin):
    platform: str
    run: Command
    image_resource: Optional[Resource] = None
    inputs: List[Input] = field(default_factory=list)
    outputs: List[Output] = field(default_factory=list)
    caches: List[Cache] = field(default_factory=list)
    params: Dict[str, str] = field(default_factory=dict)
    rootfs_uri: Optional[str] = None
    container_limits: Optional[Container_limits] = None


class StepABC(ABC):
    @abstractmethod
    def rewrite(self, rewrites: Dict[str, str]) -> StepABC:
        pass


@yaml_object(yaml)
@dataclass
class Task(SetstateInitMixin, StepABC):
    """Concourse Task class

    :param task: Name of the task
    """

    task: str
    config: Optional[TaskConfig] = None
    file: Optional[str] = None
    image: Optional[str] = None
    priviledged: bool = False
    vars: Dict[str, str] = field(default_factory=dict)
    container_limits: Optional[Container_limits] = None
    params: Dict[str, str] = field(default_factory=dict)
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_mapping: Dict[str, str] = field(default_factory=dict)

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        if not self.config:
            raise Exception(f"Task needs config for {self}")
        if self.file:
            raise Exception(f"No support for file in {self}")

        return dataclasses.replace(
            self,
            input_mapping={input: rewrites[input] for input in self.config.inputs},
            output_mapping={output: rewrites[output] for output in self.config.outputs},
        )


@yaml_object(yaml)
@dataclass
class Get(SetstateInitMixin, StepABC):
    get: str
    resource: Optional[str] = None
    passed: List[str] = field(default_factory=list)
    params: Optional[Any] = None
    trigger: bool = False
    version: str = "latest"

    def __post_init__(self):
        if not self.resource:
            self.resource = self.get

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        return dataclasses.replace(self, get=rewrites[self.get])


@yaml_object(yaml)
@dataclass
class Put(SetstateInitMixin, StepABC):
    put: str
    resource: Optional[str] = None
    inputs: str = "all"
    params: Optional[Any] = None
    get_params: Optional[Any] = None

    def __post_init__(self):
        if not self.resource:
            self.resource = self.put

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        return dataclasses.replace(self, put=rewrites[self.put])


@yaml_object(yaml)
@dataclass
class Do(SetstateInitMixin, StepABC):
    do: List[Step]

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        return dataclasses.replace(
            self, do=[step.rewrite(rewrites) for step in self.do]
        )


@yaml_object(yaml)
@dataclass
class In_parallel(SetstateInitMixin, StepABC):
    steps: List[Step] = field(default_factory=list)
    limit: Optional[int] = None
    fail_fast: bool = False

    def rewrite(self, rewrites: Dict[str, str]) -> Get:
        return dataclasses.replace(
            self, steps=[step.rewrite(rewrites) for step in self.steps]
        )


Step = Union[Get, Put, Task, In_parallel, Do]


@yaml_object(yaml)
@dataclass
class LogRetentionPolicy(SetstateInitMixin):
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


@yaml_object(yaml)
@dataclass(order=True)
class Job(SetstateInitMixin):
    name: str
    plan: List[Step]
    old_name: Optional[str] = None
    serial: bool = False
    serial_groups: List[str] = field(default_factory=list)
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

    def exactEq(self, other: Job) -> bool:
        return self.name == other.name and self == other

    def rewrite(self, rewrites: Dict[str, str]) -> Job:
        return dataclasses.replace(
            self, plan=[step.rewrite(rewrites) for step in self.plan]
        )

    @classmethod
    def uniques_and_rewrites(
        cls, aList: List[Job], bList: List[Job]
    ) -> Tuple[List[Job], Dict[str, str]]:

        ret_list: List[Job] = aList.copy()
        appendMap: Dict[str, str] = {}

        for item in bList:
            if item in ret_list:  # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [
                resource for resource in ret_list if resource.name == item.name
            ]:  # Name already used for different item so rename it and then add
                unique_num = 0
                while [
                    resource
                    for resource in ret_list
                    if resource.name == f"{item.name}-{unique_num}"
                ]:
                    unique_num += 1

                b_name_alt = f"{item.name}-{unique_num}"
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else:  # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap

    @classmethod
    def rewrite_jobs(cls, in_jobs: List[Job], rewrites: Dict[str, str]) -> List[Job]:
        # TODO: add Job rewrites here

        jobs = [job.rewrite(rewrites) for job in in_jobs]

        # for job in jobs:
        #     for plan in job.plan:
        #         print(f'Looking at plan: {plan}')
        #         if isinstance(plan, Task):
        #             print(f'  we have a task')
        # iterate across in_list and apply rewrites identified
        # in rewrites. Return a new list.__reduce__

        # Rewrites MUST preserve inner naming convention even
        # if they mutate the outer linkages.

        # return [dataclasses.replace(job, type=rewrites[job.type]) for job in in_list]
        # print("REWRITE for job not implemented yet")

        return jobs


@yaml_object(yaml)
@dataclass
class Pipeline(SetstateInitMixin):
    """Definition of a concourse plan"""

    resource_types: list[ResourceType] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    jobs: List[Job] = field(default_factory=list)

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
    def merge(cls, pipeline_left: Pipeline, pipeline_right: Pipeline) -> Pipeline:
        """Merge two Concourse Plans

        Merge will take two Things and create a merge of them.
        It will resolve shared resources and map into a single name.
        It will resolve different resources with same name into discrete resourcess.
        The secondary plan be modified in naming, but not in function during the merge
        to achinve minimal :class:`Resource` s and :class:`ResourceType` s.

        :param aThing: Base concourse plan to add second plan to.
        This will be unchanged through merge process
        :param bThing: Secondary plan.

        :Return:
            Merged output from combination of both inputs with minimised
            :class:`Resource` s and :class:`ResourceType` s
        """
        print(f"My job is merging two jobs:\n  {pipeline_left}\n  {pipeline_right}")

        # resource_types_input = aThing.resource_types + bThing.resource_types

        if not pipeline_left.validate():
            raise Exception(f"pipeline_left is not valid: {pipeline_left}")

        if not pipeline_right.validate():
            raise Exception(f"pipeline_right is not valid: {pipeline_right}")

        resource_types, resource_types_rewrites = ResourceType.uniques_and_rewrites(
            pipeline_left.resource_types, pipeline_right.resource_types
        )

        print(f"RT = {resource_types}")
        print(f"RT rewrites = {resource_types_rewrites}")

        bThing_resource_renames = Resource.rewrite(
            pipeline_right.resources, resource_types_rewrites
        )

        resources, resource_rewrites = Resource.uniques_and_rewrites(
            pipeline_left.resources, bThing_resource_renames
        )
        print(f"R = {resources}")
        print(f"R rewrites = {resource_rewrites}")

        bThing_jobs = Job.rewrite_jobs(pipeline_right.jobs, resource_rewrites)

        jobs, job_rewrites = Job.uniques_and_rewrites(pipeline_left.jobs, bThing_jobs)

        # noqa: E501 # For the jobs. Need to recurse through the obejcts to apply rewrites to them based on resource rewrites.
        # noqa: E501 #This will result in the correctly nameed/mapped resources in teh bThing to match the merged resources.
        # noqa: E501 #Next step is to work out how to merge the jobs:
        # noqa: E501 #    1. Dont merge just keep them together (side by side). (should be simple viable optoin)
        # noqa: E501 #    2. Work out where they share name and share parts of pipeline then merge those.    (MAYBE not a good idea)

        return Pipeline(resource_types=resource_types, resources=resources, jobs=jobs)
