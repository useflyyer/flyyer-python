from urllib.parse import unquote

from flayyer import __version__, Flayyer, FlayyerMeta, to_query


def test_version():
    assert __version__ is not None


def test_url_encoding():
    flayyer = Flayyer(
        tenant="tenant",
        deck="deck",
        template="template",
        variables={"title": "Hello world!"},
    )
    href = flayyer.href()
    assert href.startswith("https://flayyer.io/v2/tenant/deck/template.jpeg?__v=")
    assert href.endswith("&title=Hello+world%21")


def test_meta_parameters():
    flayyer = Flayyer(
        tenant="tenant",
        deck="deck",
        template="template",
        variables={"title": "title"},
        meta=FlayyerMeta(
            agent="whatsapp",
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flayyer.href()
    assert href.startswith("https://flayyer.io/v2/tenant/deck/template.jpeg?__v=")
    assert href.find("&title=title") != -1
    assert href.find("&_ua=whatsapp") != -1
    assert href.find("&_w=100") != -1
    assert href.find("&_h=200") != -1
    assert href.find("&__id=dev+forgot+to+slugify") != -1


def test_simple_stringify():
    data = {"a": "hello", "b": 100, "c": False, "d": None, "b": 999}
    result = to_query(data)
    assert result == "a=hello&b=999&c=false&d="


def test_complex_stringify():
    data = {"a": {"aa": "bar", "ab": "foo"}, "b": [{"c": "foo"}, {"c": "bar"}]}
    result = to_query(data)
    assert unquote(result) == "a[aa]=bar&a[ab]=foo&b[0][c]=foo&b[1][c]=bar"
