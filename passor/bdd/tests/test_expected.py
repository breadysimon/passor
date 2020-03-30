from lib.testing import Expect


def test_expected():
    a = Expect()
    assert a.enabled
    assert a.check() == {}
    assert a.check('aaaa') == {}
    a['x'] = 1
    assert a.check('x') == 1
    assert a.check().check('aaaa') == {}

    b = Expect(None)
    assert not b.enabled

    c = Expect(a=1, b=2)
    assert c.enabled and c['a'] == 1
    d = Expect({})
    assert d == {}
    e = Expect(**c)
    assert e['a'] == 1 and e['b'] == 2
