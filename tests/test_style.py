from nose.tools import raises, eq_
from pygments.styles import STYLE_MAP, get_style_by_name
from pygments.token import STANDARD_TYPES

from pygout.style import TokenStyleEditor, create_style
from pygout.style import create_style_from_pygments


# Test each individual token style component
def test_tokenstyle_component():
    tests = [
        ('noinherit', 'inherit', True, False),
        ('bold', 'bold', None, True),
        ('nobold', 'bold', None, False),
        ('italic', 'italic', None, True),
        ('noitalic', 'italic', None, False),
        ('underline', 'underline', None, True),
        ('nounderline', 'underline', None, False),
        ('#123456', 'color', None, '#123456'),
        ('#123', 'color', None, '#112233'),
        ('bg:#123456', 'bgcolor', None, '#123456'),
        ('bg:#123', 'bgcolor', None, '#112233'),
        ('border:#123456', 'border', None, '#123456'),
        ('border:#123', 'border', None, '#112233'),
    ]

    def test(style, attr, before, after):
        s = TokenStyleEditor()
        assert getattr(s, attr) == before
        s.apply(style)
        assert getattr(s, attr) == after

    for t in tests:
        yield (test,) + t


# Test that invalid components raise an error
@raises(ValueError)
def test_tokenstyle_invalid_component():
    s = TokenStyleEditor("not:valid")


# Test some TokenStyleEditor edits that should raise errors
def test_tokenstyle_invalid_edit():
    tests = [
        ('inherit', None),
        ('bold', 'foo'),
        ('italic', 'foo'),
        ('underline', 'foo'),
        ('color', 'foo'),
        ('bgcolor', 'foo'),
        ('border', 'foo'),
    ]

    @raises(ValueError)
    def test(attr, value):
        s = TokenStyleEditor()
        setattr(s, attr, value)

    for t in tests:
        yield (test,) + t


# Test that token styles are equal when they should be
def test_tokenstyle_equality():
    s1 = TokenStyleEditor()
    # Equal to itself
    assert s1 == s1
    s2 = TokenStyleEditor()
    # Equal to another empty style
    assert s1 == s2
    s1.apply("bold noitalic #fff bg:#000")
    # Not equal to different style
    assert s1 != s2
    s2.bold = True
    s2.italic = False
    s2.color = '#ffffff'
    s2.bgcolor = '#000'
    # The styles should be equal again
    assert s1 == s2


# Test that going to and from TokenStyleEditor leaves the style unchanged
def test_tokenstyle_identity():
    styles = [
        '',
        'noinherit bg:#abc',
        '#abcdef',
        '#123 bg:#abc noinherit nobold underline',
    ]

    def test(s):
        s1 = TokenStyleEditor(s)
        s2 = TokenStyleEditor(s1)
        assert s1 == s2

    for s in styles:
        yield test, s


# Test behaviour of valid colors
# TODO: move this to test_util.py
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
        s = TokenStyleEditor("#000000")
        assert s.color != postcond, 'postcondition true before test'
        s.color = value
        eq_(s.color, postcond)

    for value, postcond in valid_colors:
        yield test, value, postcond


# Test rejection of invalid colors
# TODO: move this to test_util.py
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
        s = TokenStyleEditor()
        s.color = value

    for value in invalid_colors:
        yield test, value


# Test that the conversion from Pygments style to PygOut style is lossless
#
# TODO: Actually enable the tests... currently they fail for 2 reasons:
#       1) Pygments bug in expanding 3-digit colors
#       2) Pygments not enforcing uppercase/lowercase
#
# See: https://bitbucket.org/birkenfeld/pygments-main/changeset/c61a98b9e109
def test_style_from_pygments():
    styles = sorted(STYLE_MAP.keys())

    def compare_style_lists(style, l1, l2):
        d1 = dict(l1)
        d2 = dict(l2)
        keys = sorted(list(set(*[d1.keys() + d2.keys()])))

        for k in keys:
            assert d1[k] == d2[k], '{} != {} (style: {}, token: {})'.format(
                    d1[k], d2[k], style, k)

    def test(style):
        pygments_style = get_style_by_name(style)
        pygout_style = create_style_from_pygments(style)
        # Check that all token styles are the same - at this point they haven't
        # been via TokenStyleEditor.
        compare_style_lists(style, pygments_style.list_styles(),
                            pygout_style.list_styles())
        new_pygout_style = create_style(None, pygout_style.pygout_styles)
        # Check that a style that's gone via the TokenStyleEditor conversion
        # still is the same style.
        compare_style_lists(style, pygout_style.list_styles(),
                            new_pygout_style.list_styles())

    #for s in styles:
    #    yield test, s
