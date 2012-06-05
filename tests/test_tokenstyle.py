from nose.tools import raises, eq_

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
    s1.apply_pygments_style(str(s2))
    assert s1 == s2 == s3

    assert TokenStyle('#fff') == TokenStyle('#FFFFFF')


def test_identity():
    styles = [
        '',
        'noinherit bg:#abc',
        '#abcdef',
        '#123 bg:#abc noinherit nobold underline',
    ]

    def test_style_identity(s):
        s1 = TokenStyle(s)
        s2 = TokenStyle(str(s1))
        assert s1 == s2

    for s in styles:
        yield test_style_identity, s


def test_valid_color():
    valid_colors = [
        (None, None),               # empty
        ('', None),                 # empty
        ('#012', '#001122'),        # 3-digit, converted to 6-digit)
        ('#012345', '#012345'),     # 6-digit, preserved)
        ('#def', '#ddeeff'),        # hex letters, 3-digit
        ('#abcdef', '#abcdef'),     # hex letters, 6-digit
        ('#aBCdeF', '#abcdef'),     # mixed case -> canonical representation
        ('#AbC', '#aabbcc'),        # mixed case, 3-digit -> canonical
    ]

    def test(value, postcond):
        s = TokenStyle("#000000")
        assert s.color != postcond, 'postcondition true before test'
        s.color = value
        eq_(s.color, postcond)

    for value, postcond in valid_colors:
        yield test, value, postcond


def test_invalid_color():
    invalid_colors = [
        'red',          # Not a hex color
        '000000',       # Missing the leading #
        '#0',           # length not 3 or 6
        '#12',          # length not 3 or 6
        '#1234',        # length not 3 or 6
        '#12345',       # length not 3 or 6
        '#1234567',     # length not 3 or 6
        '#axbycz',      # invalid hex characters
    ]

    @raises(ValueError)
    def test(value):
        s = TokenStyle()
        s.color = value

    for value in invalid_colors:
        yield test, value
