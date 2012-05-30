from pygout.style import TokenStyle


def test_components():
    def test_component(c, attr, before, after):
        s = TokenStyle()
        assert getattr(s, attr) == before
        s.apply_pygments_style(c)
        assert getattr(s, attr) == after

    tests = [
        ('noinherit', 'inherit', True, False),
        ('#123456', 'color', None, '#123456'),
        ('#123', 'color', None, '#112233'),
        ('bg:#123456', 'bgcolor', None, '#123456'),
        ('bg:#123', 'bgcolor', None, '#112233'),
        ('bold', 'bold', None, True),
        ('nobold', 'bold', None, False),
        ('italic', 'italic', None, True),
        ('noitalic', 'italic', None, False),
        ('underline', 'underline', None, True),
        ('nounderline', 'underline', None, False),
    ]

    for t in tests:
        yield (test_component,) + t


def test_equality():
    s1 = TokenStyle()
    assert s1 == s1
    s2 = TokenStyle('#123 bg:#abc noinherit bold italic nounderline')
    s3 = TokenStyle('#123 bg:#abc noinherit bold italic nounderline')
    assert s2 == s3

    assert s1 != s2
    s1.apply_pygments_style(s2.to_pygments_style())
    assert s1 == s2 == s3


def test_identity():
    styles = [
        '',
        'noinherit bg:#abc',
        '#abcdef',
        '#123 bg:#abc noinherit nobold underline',
    ]

    def test_style_identity(s):
        s1 = TokenStyle(s)
        s2 = TokenStyle(s1.to_pygments_style())
        assert s1 == s2

    for s in styles:
        yield test_style_identity, s
