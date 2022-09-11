
from typing import Any, Dict, Optional, List, Union
import ruamel.yaml
from dataclasses import dataclass, field

yaml = ruamel.yaml.YAML()

@dataclass
class ResourceConfig:
    repository: str
    tag: str


yaml.register_class(ResourceConfig)



@dataclass
class ResourceType:
    name: str
    type: str
    source: ResourceConfig
    privileged: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    check_every: str = '1m'
    tags: list[str] = field(default_factory=list)
    defaults: Dict[str, Any] = field(default_factory=dict)

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


yaml.register_class(Resource)


class User(object):
    def __init__(self, name, age):
        self.name = name
        self.age = age


yaml.register_class(User)


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
class LogRetentionPolicy:
    days: int
    builds: int
    minimum_succeeded_builds: int

yaml.register_class(LogRetentionPolicy)




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

yaml.register_class(FullThing)

# def test_answer():
#     assert 5 == 5
