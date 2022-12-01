# concourseatom Copyright (C) 2022 Ben Greene
"""Test functions for Concourse data models
"""
from contextlib import nullcontext as does_not_raise


from typing import Any, Dict
from concourseatom.models import (
    Cache,
    Command,
    Container_limits,
    Do,
    Pipeline,
    Get,
    In_parallel,
    Input,
    Job,
    LogRetentionPolicy,
    Output,
    Put,
    Resource,
    ResourceType,
    Task,
    TaskConfig,
)
from textwrap import dedent
import pytest


def test_ResourceType():
    test0 = ResourceType(name="a", type="b", source={})
    assert test0 == ResourceType(name="a", type="b", source={})

    assert test0 == ResourceType(name="ax", type="b", source={})
    assert not test0.exactEq(ResourceType(name="ax", type="b", source={}))
    assert test0 != ResourceType(name="a", type="bx", source={})
    assert test0 != ResourceType(name="a", type="b", source={"d": "e"})

    assert test0 != ResourceType(name="a", type="b", source={}, privileged=True)

    resource_types, rewrites = Resource.uniques_and_rewrites(
        [
            ResourceType(name="a", type="x", source={}),
            ResourceType(name="c", type="y", source={}),
        ],
        [
            ResourceType(name="b", type="x", source={}),
            ResourceType(name="a", type="z", source={}),
        ],
    )
    assert resource_types == [
        ResourceType(name="a", type="x", source={}),
        ResourceType(name="c", type="y", source={}),
        ResourceType(name="c", type="z", source={}),
    ]
    assert rewrites == {"b": "a", "a": "a-000"}

    stream = test0.yaml()

    print(stream)

    test1 = ResourceType.parse_raw(stream)
    assert test0 == test1


@pytest.mark.parametrize(
    "list_left, list_right,expected_uniques, expected_rewrites",
    [
        ([], [], [], {}),  # Empty
        (  # Map to existing
            [
                ResourceType(name="a", type="b"),
            ],
            [
                ResourceType(name="a", type="b"),
            ],
            [
                ResourceType(name="a", type="b"),
            ],
            {
                "a": "a",
            },
        ),
        (  # Map to new
            [
                ResourceType(name="a", type="b"),
            ],
            [
                ResourceType(name="c", type="d"),
            ],
            [
                ResourceType(name="a", type="b"),
                ResourceType(name="c", type="d"),
            ],
            {
                "c": "c",
            },
        ),
        (  # Map to existing but with orig name
            [
                ResourceType(name="a", type="b"),
            ],
            [
                ResourceType(name="c", type="b"),
            ],
            [
                ResourceType(name="a", type="b"),
            ],
            {
                "c": "a",
            },
        ),
        (  # Map to new but with alt name
            [
                ResourceType(name="a", type="b"),
            ],
            [
                ResourceType(name="a", type="c"),
            ],
            [
                ResourceType(name="a", type="b"),
                ResourceType(name="a-000", type="c"),
            ],
            {
                "a": "a-000",
            },
        ),
        (  # Map to new but with alt name and increment
            [
                ResourceType(name="a", type="b"),
                ResourceType(name="a-000", type="d"),
            ],
            [
                ResourceType(name="a", type="c"),
            ],
            [
                ResourceType(name="a", type="b"),
                ResourceType(name="a-000", type="d"),
                ResourceType(name="a-001", type="c"),
            ],
            {
                "a": "a-001",
            },
        ),
    ],
)
def test_ResourceType_uniques_rewrites(
    list_left, list_right, expected_uniques, expected_rewrites
):
    uniques, rewrites = ResourceType.uniques_and_rewrites(list_left, list_right)

    assert uniques == expected_uniques
    assert all(u.exactEq(eu) for u, eu in zip(uniques, expected_uniques))
    assert rewrites == expected_rewrites


@pytest.mark.parametrize(
    "list_left, list_right,expected_uniques, expected_rewrites",
    [
        ([], [], [], {}),  # Empty
        (  # Map to existing
            [
                Job(
                    name="a",
                    plan=[
                        Get(get="b", resource="c"),
                        In_parallel(
                            steps=[
                                Get(get="c", resource="d"),
                            ]
                        ),
                        Put(put="g", resource="h"),
                    ],
                )
            ],
            [
                Job(
                    name="a",
                    plan=[
                        Get(get="b", resource="c"),
                        In_parallel(
                            steps=[
                                Get(get="e", resource="f"),
                            ]
                        ),
                        Put(put="g", resource="h"),
                    ],
                ),
            ],
            [
                Job(
                    name="a",
                    plan=[
                        Get(get="b", resource="c"),
                        In_parallel(
                            steps=[
                                Get(get="c", resource="d"),
                                Get(get="e", resource="f"),
                            ]
                        ),
                        Put(put="g", resource="h"),
                    ],
                ),
            ],
            {
                # "a": "a",
            },
        ),
    ],
)
def test_ResourceType_uniques_rewrites_deep(
    list_left, list_right, expected_uniques, expected_rewrites
):
    uniques, rewrites = ResourceType.uniques_and_rewrites(
        list_left, list_right, deep=True
    )

    assert uniques == expected_uniques
    assert all(u.exactEq(eu) for u, eu in zip(uniques, expected_uniques))
    assert rewrites == expected_rewrites


def test_Resource():
    test0 = Resource(name="a", type="b", source={})
    assert test0 == Resource(name="a", type="b", source={})

    assert test0 == Resource(name="ax", type="b", source={})
    assert not test0.exactEq(Resource(name="ax", type="b", source={}))

    assert test0 != Resource(name="a", type="bx", source={})
    assert test0 != Resource(name="a", type="b", source={"c": "d"})
    assert test0 != Resource(name="a", type="b", source={}, old_name="x")

    resources, rewrites = Resource.uniques_and_rewrites(
        [
            Resource(name="a", type="x", source={}),
            Resource(name="c", type="y", source={}),
        ],
        [
            Resource(name="b", type="x", source={}),
            Resource(name="a", type="z", source={}),
        ],
    )
    assert resources == [
        Resource(name="a", type="x", source={}),
        Resource(name="c", type="y", source={}),
        Resource(name="c", type="z", source={}),
    ]
    assert rewrites == {"b": "a", "a": "a-000"}

    stream = test0.yaml()

    print(stream)

    test1 = Resource.parse_raw(stream)
    assert test0 == test1


@pytest.mark.parametrize(
    "myObj,rewrites,output, expectation",
    [
        (Get(get="a"), {"a": "a"}, Get(get="a", resource="a"), does_not_raise()),
        (Get(get="a"), {"a": "b"}, Get(get="a", resource="b"), does_not_raise()),
        (Put(put="a"), {"a": "a"}, Put(put="a", resource="a"), does_not_raise()),
        (Put(put="a"), {"a": "b"}, Put(put="a", resource="b"), does_not_raise()),
        (Do(do=[]), {}, Do(do=[]), does_not_raise()),
        (
            Do(do=[Put(put="a")]),
            {"a": "a"},
            Do(do=[Put(put="a", resource="a")]),
            does_not_raise(),
        ),
        (
            In_parallel(In_parallel=[]),
            {},
            In_parallel(In_parallel=[]),
            does_not_raise(),
        ),
        (
            In_parallel(in_parallel=[Put(put="a")]),
            {"a": "a"},
            In_parallel(in_parallel=[Put(put="a")]),
            does_not_raise(),
        ),
        (
            Task(task="a"),
            {},
            Task(task="a"),
            pytest.raises(Exception),
        ),  # Config must be provided
        (
            Task(task="a", config=TaskConfig(platform="linux", run=Command(path="sh"))),
            {},
            Task(task="a", config=TaskConfig(platform="linux", run=Command(path="sh"))),
            does_not_raise(),
        ),
        (
            Task(
                task="a",
                config=TaskConfig(
                    platform="linux", run=Command(path="sh"), inputs=[Input(name="a")]
                ),
            ),
            {"a": "a"},
            Task(
                task="a",
                config=TaskConfig(
                    platform="linux", run=Command(path="sh"), inputs=[Input(name="a")]
                ),
                input_mapping={"a": "a"},
            ),
            does_not_raise(),
        ),
        (
            Task(
                task="a",
                config=TaskConfig(
                    platform="linux", run=Command(path="sh"), outputs=[Output(name="a")]
                ),
            ),
            {"a": "a"},
            Task(
                task="a",
                config=TaskConfig(
                    platform="linux", run=Command(path="sh"), outputs=[Output(name="a")]
                ),
                output_mapping={"a": "a"},
            ),
            does_not_raise(),
        ),
    ],
)
def test_rewrites(myObj: Any, rewrites: Dict[str, str], output: Any, expectation):
    with expectation:
        assert output == myObj.resource_rewrite(rewrites)


@pytest.mark.parametrize(
    "myClass, myYaml",
    [
        (
            ResourceType,
            """
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
            """,
        ),
        (
            Resource,
            """
                name: a
                type: b
                source:
                  abc: def
                old_name: bruce
                icon: icon1
                version: v1
                check_every: 10m
                check_timeout: 1m
                expose_build_created_by: True
                tags:
                - abc
                - def
                public: True
                webhook_token: abcd
            """,
        ),
        (
            Command,
            """
                path: r
                args:
                    - s
                dir: t
                user: v
            """,
        ),
        (
            Command,
            """
                path: ls
                args:
                    - -la
                    - ./concourse-docs-git
                dir: t
                user: v
            """,
        ),
        (
            Command,
            """
                path: ls
                args: ["-la", "./concourse-docs-git"]
                dir: t
                user: v
            """,
        ),
        (
            Input,
            """
                name: a
                path: b
                optional: True
            """,
        ),
        (
            Output,
            """
                name: 1
                path: b
            """,
        ),
        (
            Cache,
            """
                path: b
            """,
        ),
        (
            Container_limits,
            """
                cpu: 1
                memory: 2
            """,
        ),
        (
            TaskConfig,
            """
                platform: a
                image_resource:
                  name: a
                  type: b
                  source: {}
                run:
                  path: d
                inputs:
                - name: e
                outputs:
                - name: f
                caches:
                - path: g
                params:
                  h: i
                rootfs_uri: j
                container_limits:
                  cpu: 1
                  memory: 2
            """,
        ),
        (
            Task,
            """
                task: a
                config:
                  platform: str
                  image_resource:
                    name: b
                    type: c
                    source: {}
                  run:
                    path: d
                file: e
                image: f
                priviledged: True
                vars:
                  g: h
                container_limits:
                  cpu: 1
                  memory: 2
                params:
                  i: j
                input_mapping:
                  k: l
                output_mapping:
                  m: n
            """,
        ),
        (
            Get,
            """
                get: a
                resource: b
                passed:
                - d
                params:
                  e: f
                trigger: True
                version: g
            """,
        ),
        (
            Put,
            """
                put: a
                resource: b
                inputs: c
                params:
                  d: e
                get_params:
                  f: g
            """,
        ),
        (
            Do,
            """
                do:
                - get: a
            """,
        ),
        (
            In_parallel,
            """
                steps:
                - get: a
                limit: 1
                fail_fast: True
            """,
        ),
        (
            LogRetentionPolicy,
            """
                days: 1
                builds: 2
                minimum_succeeded_builds: 3
            """,
        ),
        (
            Job,
            """
                name: a
                plan:
                - get: b
                old_name: b
                serial: True
                serial_groups:
                - c
                max_in_flight: 1
                build_log_retention:
                  days: 1
                  builds: 2
                  minimum_succeeded_builds: 3
                public: True
                disable_manual_trigger: True
                interruptible: True
            """,
        ),
    ],
)
def test_read_classes(myClass, myYaml):
    loadyaml_a = dedent(myYaml)
    print(f"Loading from yaml {loadyaml_a}")
    test0 = myClass.parse_raw(loadyaml_a)
    print(f"Read as {test0}")

    assert isinstance(test0, myClass)

    stream = test0.yaml()

    print(stream)

    test1 = myClass.parse_raw(stream)
    assert test0 == test1


def test_Job():
    test0 = Job(name="a", plan=[])
    assert test0 == Job(name="a", plan=[])

    assert test0 == Job(name="ax", plan=[])
    assert test0 != Job(name="ax", plan=[], old_name="ax")

    test0 = Job(
        name="a",
        plan=[
            Put(put="a"),
            Get(get="b"),
        ],
    )

    stream = test0.yaml()

    print(stream)

    test1 = Job.parse_raw(stream)
    assert test0 == test1


@pytest.mark.parametrize(
    "yaml_l, yaml_r, yaml_merged",
    [
        (  # Empty content merge
            """
            resource_types: []
            resources: []
            jobs: []
            """,
            """
            resource_types: []
            resources: []
            jobs: []
            """,
            """
            resource_types: []
            resources: []
            jobs: []
            """,
        ),
        (  # LHS provide content
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types: []
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
        ),
        (  # RHS provide content
            """
            resource_types: []
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
        ),
        (  # Merge identical values
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
        ),
        (  # Merge identical types (priorities name to be LHS)
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: b
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
        ),
        (  # Merge identical names (differing content to generate new name)
            """
            resource_types:
            - name: a
              type: a1
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a2
            resources: []
            jobs: []
            """,
            """
            resource_types:
            - name: a
              type: a1
            - name: a-000
              type: a2
            resources: []
            jobs: []
            """,
        ),
        (  # Merge XXXXXX
            """
            resource_types:
            - name: a
              type: a1
            resources:
            - name: g
              type: a
              source: {}
            jobs:
            - name: k
              plan:
              - get: g
              - put: g
            """,
            """
            resource_types:
            - name: a
              type: a2
            resources:
            - name: g
              type: a
              source: {}
            jobs:
            - name: l
              plan:
              - get: g
              - put: g
            """,
            """
            resource_types:
            - name: a
              type: a1
            - name: a-000
              type: a2
            resources:
            - name: g
              type: a
              source: {}
            - name: g-000
              type: a-000
              source: {}
            jobs:
            - name: k
              plan:
              - get: g
              - put: g
            - name: l
              plan:
              - get: g
                resource: g-000
              - put: g
                resource: g-000
            """,
        ),
    ],
)
def test_merge_pipelines(yaml_l, yaml_r, yaml_merged):

    test_l = Pipeline.parse_raw(dedent(yaml_l))
    test_r = Pipeline.parse_raw(dedent(yaml_r))

    merged_expected = Pipeline.parse_raw(dedent(yaml_merged))

    merged = Pipeline.merge(test_l, test_r)

    print(merged.yaml())

    assert merged_expected == merged
    assert merged_expected.exactEq(merged)


@pytest.mark.parametrize(
    "myYaml",
    [
        (
            """
            jobs:
            - name: job
              public: true
              plan:
              - task: simple-task
                config:
                  platform: linux
                  image_resource:
                    type: registry-image
                    source: { repository: busybox }
                  run:
                    path: echo
                    args: ["Hello world!"]
            """
        ),
        (
            """
            resources:
            - name: concourse-docs-git
              type: git
              icon: github
              source:
                uri: https://github.com/concourse/docs

            jobs:
            - name: job
              public: true
              plan:
              - get: concourse-docs-git
                trigger: true
              - task: list-files
                config:
                  inputs:
                    - name: concourse-docs-git
                  platform: linux
                  image_resource:
                    type: registry-image
                    source: { repository: busybox }
                  run:
                    path: ls
                    args: ["-la", "./concourse-docs-git"]
            """
        ),
    ],
)
def test_jobSampleLoad(myYaml):
    print(f"Loaded job is {myYaml}")
    test_a = Pipeline.parse_raw(myYaml)
    print(f"Read as {test_a}")


def test_Pipeline_load():
    loadyaml_a = dedent(
        """
        resource_types:
        - name: a
          type: b
          source:
            c: d
          privileged: True
          params:
            e: f
          check_every: 10m
          tags:
          - g
          defaults:
            i: j
        resources:
        - name: a
          type: b
          source:
            c: d
          old_name: e
          icon: f
          version: g
          check_every: 10m
          check_timeout: 2h
          expose_build_created_by: True
          tags:
          - h
          public: True
          webhook_token: j
        jobs:
        - name: a
          plan:
          - get: b
            resource: c
            passed:
            - d
            params:
              e: f
            trigger: True
            version: "1"
          - put: g
            resource: h
            inputs: i
            params:
              j: k
            get_params:
              l: m
          - task: n
            config:
              platform: o
              image_resource:
                p: q
              run:
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
                cpu: 1
                memory: 2
            file: b1
            image: c1
            priviledged: True
            vars:
              d1: e1
            container_limits:
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
        """
    )
    print(f"Loaded job is {loadyaml_a}")
    test_a = Pipeline.parse_raw(loadyaml_a)
    print(f"Read as {test_a}")


@pytest.mark.parametrize(
    "myyaml, valid",
    [
        (
            """
            resource_types: []
            resources: []
            jobs: []
            """,
            True,
        ),
        (
            """
            resource_types: []
            resources:
            - name: a
              type: b
              source: {}
            jobs: []
            """,
            False,
        ),
        (
            """
            resource_types:
            - name: b
              type: c
            resources:
            - name: a
              type: b
              source: {}
            jobs: []
            """,
            True,
        ),
    ],
)
def test_pipeline_validate(myyaml: str, valid: bool):
    obj_left = Pipeline.parse_raw(dedent(myyaml))

    assert obj_left.validate() == valid
