



import io
from models import Get, Job, Put, Resource, ResourceConfig, ResourceType
import ruamel.yaml
from textwrap import dedent, indent

yaml = ruamel.yaml.YAML()


def test_ResourceConfig():
    test0 = ResourceConfig('a', 'b')
    assert test0 == ResourceConfig('a', 'b')

    assert test0 != ResourceConfig('ax', 'b')
    assert test0 != ResourceConfig('a', 'bx')
    assert test0 != ResourceConfig('ax', 'bx')

    stream= io.StringIO()
    yaml.dump(test0, stream)

    test1 = yaml.load(stream.getvalue())
    print(test1)
    assert test0 == test1

    # assert stream.getvalue() == dedent("""\
    #     !ResourceConfig
    #     repository: a
    #     tag: b
    #     """)


    # print(stream.getvalue())

    # data = yaml.load(dedent("""\
    #     !ResourceConfig
    #     repository: a
    #     tag: b
    #     """))
    # print(data)




def test_ResourceType():
    test0 = ResourceType('a', 'b', ResourceConfig('c', 'd'))
    assert test0 == ResourceType('a', 'b', ResourceConfig('c', 'd'))

    assert test0 != ResourceType('ax', 'b', ResourceConfig('c', 'd'))
    assert test0 != ResourceType('a', 'bx', ResourceConfig('c', 'd'))
    assert test0 != ResourceType('a', 'b', ResourceConfig('cx', 'd'))
    assert test0 != ResourceType('a', 'b', ResourceConfig('c', 'dx'))

    assert test0 != ResourceType('a', 'b', ResourceConfig('c', 'dx'),True)


def test_Resource():
    test0 = Resource('a', 'b', {})
    assert test0 == Resource('a', 'b', {})

    assert test0 != Resource('ax', 'b', {})
    assert test0 != Resource('a', 'bx', {})
    assert test0 != Resource('a', 'b', {"c": "d"})
    assert test0 != Resource('a', 'bx', {}, 'x')

def test_Job():
    test0 = Job('a', [])
    assert test0 == Job('a', [])

    assert test0 != Job('ax', [])
    assert test0 != Job('ax', [])

    test0 = Job('a',[
        Put('a'),
        Get('b'),
    ])