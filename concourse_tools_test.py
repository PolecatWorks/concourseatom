



import io
from queue import Full
from models import FullThing, Get, Job, Put, Resource, ResourceType
import ruamel.yaml
from textwrap import dedent, indent

yaml = ruamel.yaml.YAML()


# def test_ResourceConfig():
#     test0 = ResourceConfig('a', 'b')
#     assert test0 == ResourceConfig('a', 'b')

#     assert test0 != ResourceConfig('ax', 'b')
#     assert test0 != ResourceConfig('a', 'bx')
#     assert test0 != ResourceConfig('ax', 'bx')

#     stream= io.StringIO()
#     yaml.dump(test0, stream)

#     test1 = yaml.load(stream.getvalue())
#     print(test1)
#     assert test0 == test1

#     # assert stream.getvalue() == dedent("""\
#     #     !ResourceConfig
#     #     repository: a
#     #     tag: b
#     #     """)


#     # print(stream.getvalue())

#     # data = yaml.load(dedent("""\
#     #     !ResourceConfig
#     #     repository: a
#     #     tag: b
#     #     """))
#     # print(data)




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



def test_Job():
    test0 = Job('a', [])
    assert test0 == Job('a', [])

    assert test0 != Job('ax', [])
    assert test0 != Job('ax', [])

    test0 = Job('a',[
        Put('a'),
        Get('b'),
    ])



def test_FullThing():
    test0 = FullThing(
        resource_types=[
            ResourceType('a', 'x', {}),
        ],
        resources=[
            # Resource('a', 'b', {}),
        ],
        jobs=[]
        )
    assert test0 == FullThing(
        resource_types=[
            ResourceType('a', 'x', {}),
        ],
        resources=[
            # Resource('a', 'b', {}),
        ],
        jobs=[]
        )


    test1 = FullThing(
        resource_types=[
            ResourceType('b', 'x', {}),
            ResourceType('c', 'y', {}),
        ],
        resources=[
            # Resource('a', 'b', {}),
            # Resource('ax', 'b', {}),
        ],
        jobs=[]
        )

    merged = FullThing.merge(test0, test1)

    print(merged)
