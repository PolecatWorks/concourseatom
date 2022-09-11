



from models import Get, Job, Put, Resource, ResourceConfig, ResourceType


def test_ResourceConfig():
    test0 = ResourceConfig('a', 'b')
    assert test0 == ResourceConfig('a', 'b')

    assert test0 != ResourceConfig('ax', 'b')
    assert test0 != ResourceConfig('a', 'bx')
    assert test0 != ResourceConfig('ax', 'bx')

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