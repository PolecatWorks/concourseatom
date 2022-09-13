
from __future__ import annotations
from typing import Any, Dict, Optional, List, Tuple, Union
import ruamel.yaml
from dataclasses import dataclass, field

# from typing import Self


yaml = ruamel.yaml.YAML()



@dataclass
class ResourceType:
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

yaml.register_class(ResourceType)


@dataclass
class Resource:
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
        pass
        # return [resource]

yaml.register_class(Resource)



@dataclass
class Command:
    path: str
    args: List[str] = field(default_factory=list)
    dir: Optional[str] = None
    user: Optional[str] = None

@dataclass
class Input:
    name: str
    path: Optional[str] = None
    optional: bool = False

    def __post_init__(self):
        if not self.path:
            self.path = self.name

@dataclass
class Output:
    name: str
    path: Optional[str] = None

    def __post_init__(self):
        if not self.path:
            self.path = self.name


@dataclass
class Cache:
    path: str


@dataclass
class Container_limits:
    cpu: int
    memory: int


@dataclass
class TaskConfig:
    platform: str
    image_resource: Any
    run: Command
    inputs: List[Input] = field(default_factory=list)
    outputs: List[Output] = field(default_factory=list)
    caches: List[Cache] = field(default_factory=list)
    params: Dict[str, str] = field(default_factory=dict)
    rootfs_uri: Optional[str] = None
    container_limits: Optional[Container_limits] = None



@dataclass
class Task:
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



@dataclass
class Get:
    get: str
    resource: Optional[str] = None
    passed: List[str] = field(default_factory=list)
    params: Optional[Any] = None
    trigger: bool = False
    version: str = 'latest'

    def __post_init__(self):
        if not self.resource:
            self.resource = self.get


@dataclass
class Put:
    put: str
    resource: Optional[str] = None
    inputs: str = 'all'
    params: Optional[Any] = None
    get_params: Optional[Any] = None

    def __post_init__(self):
        if not self.resource:
            self.resource = self.put



@dataclass
class In_parallel:
    steps: List[Union[Get, Put, Task]] = field(default_factory=list)
    limit: Optional[int] = None
    fail_fast: bool = False


@dataclass
class LogRetentionPolicy:
    days: int
    builds: int
    minimum_succeeded_builds: int

yaml.register_class(LogRetentionPolicy)







@dataclass
class Job:
    name: str
    plan: List[Union[Task, Get, Put]]
    old_name: Optional[str] = None
    serial: bool = False
    serial_groups: List[str] = field(default_factory=list)
    max_in_flight: Optional[int] = None
    build_log_retention: Optional[LogRetentionPolicy] = None
    pubic: bool = False
    disable_manual_trigger: bool = False
    interruptible: bool = False
    # on_success: Optional[Step] = None
    # on_failure: Optional[Step] = None
    # on_error: Optional[Step] = None
    # on_abort: Optional[Step] = None
    # ensure: Optional[Step] = None


yaml.register_class(Job)






yaml.register_class(Job)


@dataclass
class FullThing:

    resource_types: list[ResourceType] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    jobs: List[Job] = field(default_factory=list)

    @classmethod
    def merge(cls, aThing: FullThing, bThing: FullThing) -> FullThing:
        """
        Merge will take two Things and create a merge of them.
        It will resolve shared resources and map into a single name.
        It will resolve different resources with same name into discrete resourcess.
        """
        print(f'My job is merging two jobs:\n  {aThing}\n  {bThing}')

        # resource_types_input = aThing.resource_types + bThing.resource_types

        resource_types, resource_types_rewrites = ResourceType.uniques_and_rewrites(aThing.resource_types, bThing.resource_types)

        print(f'RT = {resource_types}')
        print(f'RT rewrites = {resource_types_rewrites}')



        # resources_input = Resource.rewrite(aThing.resources + bThing.resources, resource_types_rewrites)
        resources, resource_rewrites = Resource.uniques_and_rewrites(aThing.resources, bThing.resources)
        print(f'R = {resources}')
        print(f'R rewrites = {resource_rewrites}')


        resources = aThing.resources.copy()

        for resource in bThing.resources:
            if resource in resources:
                print(f'Resource {resource} already exists')
            else:
                resources.append(resource)



        return FullThing(
            resource_types=[],
            resources=resources,
            jobs=[]
            )


yaml.register_class(FullThing)

# def test_answer():
#     assert 5 == 5
