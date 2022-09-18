"""Test functions for Concourse data models
"""



import io
from queue import Full
from concourse.models import Cache, Command, Container_limits, Do, FullThing, Get, In_parallel, Input, Job, LogRetentionPolicy, Output, Put, Resource, ResourceType, Task, TaskConfig
import ruamel.yaml
from textwrap import dedent
import pytest

yaml = ruamel.yaml.YAML()




def test_ResourceType():
    test0 = ResourceType('a', 'b', {})
    assert test0 == ResourceType('a', 'b', {})

    assert test0 == ResourceType('ax', 'b', {})
    assert not test0.exactEq(ResourceType('ax', 'b', {}))
    assert test0 != ResourceType('a', 'bx', {})
    assert test0 != ResourceType('a', 'b', {'d': 'e'})

    assert test0 != ResourceType('a', 'b', {} ,True)

    resource_types, rewrites = Resource.uniques_and_rewrites([
        ResourceType('a', 'x', {}),
        ResourceType('c', 'y', {}),
    ], [
        ResourceType('b', 'x', {}),
        ResourceType('a', 'z', {}),
    ])
    assert resource_types == [
        ResourceType('a', 'x', {}),
        ResourceType('c', 'y', {}),
        ResourceType('c', 'z', {}),
    ]
    assert rewrites == {
        'b': 'a',
        'a': 'a-0'
    }

    stream= io.StringIO()
    yaml.dump(test0, stream)

    print(stream.getvalue())

    test1 = yaml.load(stream.getvalue())
    assert test0 == test1




def test_Resource():
    test0 = Resource('a', 'b', {})
    assert test0 == Resource('a', 'b', {})

    assert test0 == Resource('ax', 'b', {})
    assert not test0.exactEq(Resource('ax', 'b', {}))

    assert test0 != Resource('a', 'bx', {})
    assert test0 != Resource('a', 'b', {"c": "d"})
    assert test0 != Resource('a', 'b', {}, 'x')

    resources, rewrites = Resource.uniques_and_rewrites([
        Resource('a', 'x', {}),
        Resource('c', 'y', {}),
    ], [
        Resource('b', 'x', {}),
        Resource('a', 'z', {}),
    ])
    assert resources == [
        Resource('a', 'x', {}),
        Resource('c', 'y', {}),
        Resource('c', 'z', {}),
    ]
    assert rewrites == {
        'b': 'a',
        'a': 'a-0'
    }


    stream= io.StringIO()
    yaml.dump(test0, stream)

    print(stream.getvalue())

    test1 = yaml.load(stream.getvalue())
    assert test0 == test1





@pytest.mark.parametrize("myClass, myYaml", [
    (ResourceType,
    """ !ResourceType
        name: a
        type: b
        source:
          abc: def
        privileged: True
        params:
          abb: ddd
        check_every: 10m
        tags:
        - abc
        - def
        defaults:
          acc: rby
          add: fhfh
    """),
    (Resource,
    """ !Resource
        name: a
        type: b
        source:
          abc: def
        old_name: bruce
        ico: icon1
        version: v1
        check_every: 10m
        check_timeout: 1m
        expose_build_created_by: True
        tags:
        - abc
        - def
        public: True
        webhook_token: abcd
    """),
    (Command,
    """!Command
        path: r
        args:
            - s
        dir: t
        user: v
    """),
    (Input,
    """ !Input
        name: a
        path: b
        optional: True
    """),
    (Output,
    """!Output
        name: 1
        path: b
    """),
    (Cache,
    """ !Cache
        path: b
    """),
    (Container_limits,
    """ !Container_limits
        cpu: 1
        memory: 2
    """),
    (TaskConfig,
    """ !TaskConfig
        platform: a
        image_resource:
          b: c
        run:
          !Command
          path: d
        inputs:
        - e
        outputs:
        - f
        caches:
        - g
        params:
          h: i
        rootfs_uri: j
        container_limits:
          !Container_limits
          cpu: 1
          memory: 2
    """),
    (Task,
    """ !Task
        task: a
        config:
          !TaskConfig
          platform: str
          image_resource:
            b: c
          run:
            path: d
        file: e
        image: f
        priviledged: True
        vars:
          g: h
        container_limits:
          !Container_limits
          cpu: 1
          memory: 2
        params:
          i: j
        input_mapping:
          k: l
        output_mapping:
          m: n
    """),
    (Get,
    """ !Get
        get: a
        resource:
          b: c
        passed:
        - d
        params:
          e: f
        trigger: True
        version: g
    """),
    (Put,
    """ !Put
        put: a
        resource: b
        inputs: c
        params:
          d: e
        get_params:
          f: g
    """),
    (Do,
    """ !Do
        do:
        - !Get
          get: a
    """),
    (In_parallel,
    """ !In_parallel
        steps:
        - !Get
          get: a
        limit: 1
        fail_fast: True
    """),
    (LogRetentionPolicy,
    """ !LogRetentionPolicy
        days: 1
        builds: 2
        minimum_succeeded_builds: 3
    """),
    (Job,
    """ !Job
        name: a
        plan:
        - !Get
          get: b
        old_name: b
        serial: True
        serial_groups:
        - c
        max_in_flight: 1
        build_log_retention:
          !LogRetentionPolicy
          days: 1
          builds: 2
          minimum_succeeded_builds: 3
        public: True
        disable_manual_trigger: True
        interruptible: True
    """),

    ])
def test_read_classes(myClass, myYaml):
    loadyaml_a = dedent(myYaml)
    print(f'Loading from yaml {loadyaml_a}')
    test0 = yaml.load(loadyaml_a)
    print(f'Read as {test0}')

    assert isinstance(test0, myClass)

    stream= io.StringIO()
    yaml.dump(test0, stream)

    print(stream.getvalue())

    test1 = yaml.load(stream.getvalue())
    assert test0 == test1




def test_Job():
    test0 = Job('a', [])
    assert test0 == Job('a', [])

    assert test0 == Job('ax', [])
    assert test0 != Job('ax', [], 'ax')

    test0 = Job('a',[
        Put('a'),
        Get('b'),
    ])

    stream= io.StringIO()
    yaml.dump(test0, stream)

    print(stream.getvalue())

    test1 = yaml.load(stream.getvalue())
    assert test0 == test1


def test_FullThing():
    test0 = FullThing(
        resource_types=[
            ResourceType('a', 'x', {}),
        ],
        resources=[
            Resource('b', 'a', {}),
        ],
        jobs=[]
        )

    assert test0 == FullThing(
        resource_types=[
            ResourceType('a', 'x', {}),
        ],
        resources=[
            Resource('b', 'a', {}),
        ],
        jobs=[]
        )



    test1 = FullThing(
        resource_types=[
            ResourceType('b', 'x', {}),
            ResourceType('c', 'y', {}),
        ],
        resources=[
            Resource('a', 'b', {}),
            Resource('ax', 'c', {}),
        ],
        jobs=[]
        )

    merged = FullThing.merge(test0, test1)

    print(merged)


    stream= io.StringIO()
    yaml.dump(test0, stream)

    print(stream.getvalue())

    test1 = yaml.load(stream.getvalue())
    assert test0 == test1


def test_FullThing_load():
    loadyaml_a =  dedent("""\
        !FullThing
        resource_types:
        - !ResourceType
          name: a
          type: b
          source:
            c: d
          privileged: True
          params:
            e: f
          check_every: 10m
          tags:
            g: h
          defaults:
            i: j
        resources:
        - !Resource
          name: a
          type: b
          source:
            c: d
          old_name: e
          ico: f
          version: g
          check_every: 10m
          check_timeout: 2h
          expose_build_created_by: True
          tags:
            h: i
          public: True
          webhook_token: j
        jobs:
        - !Job
          name: a
          plan:
          - !Get
            get: b
            resource: c
            passed:
            - d
            params:
              e: f
            trigger: True
            version: "1"
          - !Put
            put: g
            resource: h
            inputs: i
            params:
              j: k
            get_params:
              l: m
          - !Task
            task: n
            config:
              !TaskConfig
              platform: o
              image_resource:
                p: q
              run:
                !Command
                path: r
                args:
                  - s
                dir: t
                user: v
              inputs:
              - w
              outputs:
              - x
              caches:
              - y
              params:
              - z
              rootfs_uri: a1
              container_limits:
                !Container_limits
                cpu: 1
                memory: 2
            file: b1
            image: c1
            priviledged: True
            vars:
              d1: e1
            container_limits:
              !Container_limits
              cpu: 3
              memory: 4
            params:
              f1: g1
            input_mapping:
              h1: j1
            output_mapping:
              k1: l1
          old_name: m1
          serial: True

        """)
    print(f'Loaded job is {loadyaml_a}')
    test_a = yaml.load(loadyaml_a)
    print(f'Read as {test_a}')



def test_FullThing_merge():

    loadyaml_a =  dedent("""\
        !FullThing
        resource_types: []
        resources: []
        jobs: []
        """)

    print(f'merge yaml from = \n{loadyaml_a}')

    test_a = yaml.load(loadyaml_a)

    print(f'merge read a = {test_a}')

    test_b = yaml.load(dedent("""
        !FullThing
        resource_types:
        - !ResourceType
          name: a
          type: a
          source: {}
        - !ResourceType
          name: b
          type: b
          source: {}
        resources: []
        jobs:
        - !Job
          name: a
          plan: []
        - !Job
          name: b
          plan:
          - !Get
            get: myget

    """))

    print(f'merge read b = {test_b}')

    merged = FullThing.merge(test_a, test_b)

    stream= io.StringIO()
    yaml.dump(merged, stream)
    print(f'Merged full = {stream.getvalue()}')