"""Data models for working with concourse data obejects
"""

from __future__ import annotations # This enables forward reference of types
import dataclasses
from typing import Any, Dict, Optional, List, Tuple, Union
from ruamel.yaml import yaml_object, YAML

from dataclasses import dataclass, field, fields


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
    return ['shells', 'gorgonzola', 'parsley']



class SetstateInitMixin:
    """Inject setstate function to class via a mixin"""
    def __setstate__(self, state):
        """Call init here so that yaml.load correctly initialises the objects. This can be a performance penalty"""
        self.__init__(**state)


@yaml_object(yaml)
@dataclass
class ResourceType(SetstateInitMixin):
    name: str
    type: str
    source: Dict[str, Any] = field(default_factory=dict)
    privileged: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    check_every: str = '1m'
    tags: list[str] = field(default_factory=list)
    defaults: Dict[str, Any] = field(default_factory=dict)

    def __eq__(self, other: ResourceType) -> bool:
        return self.type == other.type and self.source == other.source and self.privileged == other.privileged \
            and self.params == other.params and self.check_every == other.check_every and self.tags == other.tags \
            and self.defaults == other.defaults

    def exactEq(self, other: ResourceType) -> bool:
        return self.name == other.name and self == other

    @classmethod
    def uniques_and_rewrites(cls, aList: List[ResourceType], bList: List[ResourceType]) -> Tuple[List[ResourceType],Dict[str,str]]:
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
            if item in ret_list: # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [resource for resource in ret_list if resource.name == item.name]: # Name already used for different item so rename it and then add
                b_name_alt = 'fff'
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else: # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap


    # @classmethod
    # def uniques_and_rewrites(cls, in_list: List[ResourceType]) -> List[ResourceType]:
    #     """
    #     Return list of unique items and rewrites for those that are duplicates
    #     ToDo: Also need to check for reuse of names
    #     """
    #     ret_list: List[ResourceType] = []
    #     rewrites: Dict[str, str] = {}

    #     for item in in_list:
    #         if item in ret_list:
    #             rewrites[item.name] = next(obj.name for obj in in_list if obj == item)
    #         else:
    #             ret_list.append(item)

    #     return ret_list, rewrites

# yaml.register_class(ResourceType)


@yaml_object(yaml)
@dataclass
class Resource(SetstateInitMixin):
    name: str
    type: str
    source: Dict[str, Any]
    old_name: Optional[str] = None
    ico: Optional[str] = None
    version: Optional[str] = None
    check_every: str = '1m'
    check_timeout: str = '1h'
    expose_build_created_by: bool = False
    tags: list[str] = field(default_factory=list)
    public: bool = False
    webhook_token: Optional[str] = None

    def __eq__(self, other: Resource) -> bool:
        return self.type == other.type and self.source == other.source and self.old_name == other.old_name \
            and self.ico == other.ico and self.version == other.version and self.check_every == other.check_every \
            and self.check_timeout == other.check_timeout and self.expose_build_created_by == other.expose_build_created_by \
            and self.tags == other.tags and self.public == other.public and self.webhook_token == other.webhook_token

    def exactEq(self, other: Resource) -> bool:
        return self.name == other.name and self == other


    @classmethod
    def uniques_and_rewrites(cls, aList: List[Resource], bList: List[Resource]) -> Tuple[List[Resource],Dict[str,str]]:

        ret_list: List[Resource] = aList.copy()
        appendMap: Dict[str, str] = {}

        for item in bList:
            if item in ret_list: # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [resource for resource in ret_list if resource.name == item.name]: # Name already used for different item so rename it and then add
                unique_num = 0
                while [resource for resource in ret_list if resource.name == f'{item.name}-{unique_num}']:
                    unique_num+=1

                b_name_alt = f'{item.name}-{unique_num}'
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else: # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap

    # @classmethod
    # def uniques_and_rewrites(cls, in_list: List[Resource]) -> List[Resource]:
    #     """
    #     Return list of unique items and rewrites for those that are duplicates
    #     """
    #     ret_list: List[Resource] = []
    #     rewrites: Dict[str, str] = {}

    #     for item in in_list:
    #         if item in ret_list:
    #             rewrites[item.name] = next(obj.name for obj in in_list if obj == item)
    #         else:
    #             ret_list.append(item)

    #     return ret_list, rewrites

    #     resources_input = Resource.rewrite(aThing.resources + bThing.resources, resource_types_rewrites)


    @classmethod
    def rewrite(cls, in_list: List[Resource], rewrites: Dict[str, str]) -> List[Resource]:

        return [dataclasses.replace(resource, type=rewrites[resource.type]) for resource in in_list]





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



@yaml_object(yaml)
@dataclass
class Task(SetstateInitMixin):
    """Concourse Task class

    :param task: Name of the task
    :type task: str
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



@yaml_object(yaml)
@dataclass
class Get(SetstateInitMixin):
    get: str
    resource: Optional[str] = None
    passed: List[str] = field(default_factory=list)
    params: Optional[Any] = None
    trigger: bool = False
    version: str = 'latest'

    def __post_init__(self):
        if not self.resource:
            self.resource = self.get


@yaml_object(yaml)
@dataclass
class Put(SetstateInitMixin):
    put: str
    resource: Optional[str] = None
    inputs: str = 'all'
    params: Optional[Any] = None
    get_params: Optional[Any] = None

    def __post_init__(self):
        if not self.resource:
            self.resource = self.put


@yaml_object(yaml)
@dataclass
class Do(SetstateInitMixin):
    do: List[Step]


@yaml_object(yaml)
@dataclass
class In_parallel(SetstateInitMixin):
    steps: List[Step] = field(default_factory=list)
    limit: Optional[int] = None
    fail_fast: bool = False


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
@dataclass
class Job(SetstateInitMixin):
    name: str
    plan: List[Union[Task, Get, Put]]
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
        return self.plan == other.plan and self.old_name == other.old_name and self.serial == other.serial \
            and self.serial_groups == other.serial_groups and self.max_in_flight == other.max_in_flight and self.build_log_retention == other.build_log_retention \
            and self.public == other.public and self.disable_manual_trigger == other.disable_manual_trigger \
            and self.interruptible == other.interruptible

    def exactEq(self, other: Job) -> bool:
        return self.name == other.name and self == other


    @classmethod
    def uniques_and_rewrites(cls, aList: List[Job], bList: List[Job]) -> Tuple[List[Job],Dict[str,str]]:

        ret_list: List[Job] = aList.copy()
        appendMap: Dict[str, str] = {}

        for item in bList:
            if item in ret_list: # Item already exists so just map it
                appendMap[item.name] = next(obj.name for obj in ret_list if obj == item)
            elif [resource for resource in ret_list if resource.name == item.name]: # Name already used for different item so rename it and then add
                unique_num = 0
                while [resource for resource in ret_list if resource.name == f'{item.name}-{unique_num}']:
                    unique_num+=1

                b_name_alt = f'{item.name}-{unique_num}'
                # todo: check alt is unique in ret_list
                appendMap[item.name] = b_name_alt
                item.name = b_name_alt
                ret_list.append(item)
            else: # Item is unique so add it
                appendMap[item.name] = item.name
                ret_list.append(item)

        return ret_list, appendMap

    @classmethod
    def rewrite(cls, in_list: List[Job], rewrites: Dict[str, str]) -> List[Job]:

        # return [dataclasses.replace(job, type=rewrites[job.type]) for job in in_list]
        print(f'REWRITE for job not implemented yet')
        return in_list



@yaml_object(yaml)
@dataclass
class FullThing:
    """Definition of a concourse plan
    """

    resource_types: list[ResourceType] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    jobs: List[Job] = field(default_factory=list)

    @classmethod
    def merge(cls, aThing: FullThing, bThing: FullThing) -> FullThing:
        """Merge two Concourse Plans

        Merge will take two Things and create a merge of them.
        It will resolve shared resources and map into a single name.
        It will resolve different resources with same name into discrete resourcess.

        :param aThing: Base concourse plan to add second plan to. This will be unchanged through merge process
        :param bThing: Secondary plan. This may be modified in naming, but not in function during the merge to achinve minimal :class:`Resource` s and :class:`ResourceType` s.

        :Return: Merged output from combination of both inputs with minimised :class:`Resource` s and :class:`ResourceType` s
        """
        print(f'My job is merging two jobs:\n  {aThing}\n  {bThing}')

        # resource_types_input = aThing.resource_types + bThing.resource_types

        resource_types, resource_types_rewrites = ResourceType.uniques_and_rewrites(aThing.resource_types, bThing.resource_types)

        print(f'RT = {resource_types}')
        print(f'RT rewrites = {resource_types_rewrites}')

        bThing_resource_renames = Resource.rewrite(bThing.resources, resource_types_rewrites)

        # resources_input = Resource.rewrite(aThing.resources + bThing.resources, resource_types_rewrites)
        resources, resource_rewrites = Resource.uniques_and_rewrites(aThing.resources, bThing_resource_renames)
        print(f'R = {resources}')
        print(f'R rewrites = {resource_rewrites}')

        bThing_jobs = Job.rewrite(bThing.jobs, resource_rewrites)

        jobs, job_rewrites = Job.uniques_and_rewrites(aThing.jobs, bThing_jobs)


        # For the jobs. Need to recurse through the obejcts to apply rewrites to them based on resource rewrites.
        # This will result in the correctly nameed/mapped resources in teh bThing to match the merged resources.
        # Next step is to work out how to merge the jobs:
        #     1. Dont merge just keep them together (side by side). (should be simple viable optoin)
        #     2. Work out where they share name and share parts of pipeline then merge those.    (MAYBE not a good idea)
        #     3.




        return FullThing(
            resource_types=resource_types,
            resources=resources,
            jobs=jobs
            )
