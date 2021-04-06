from urllib.parse import unquote
from re import match

from flayyer import __version__, Flayyer, FlayyerMeta, to_query, FlayyerAI


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
    assert href == str(flayyer)


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
    assert href.find("&_res=") == -1


def test_simple_stringify():
    data = {"a": "hello", "b": 100, "c": False, "d": None, "b": 999}
    result = to_query(data)
    assert result == "a=hello&b=999&c=false"


def test_complex_stringify():
    data = {"a": {"aa": "bar", "ab": "foo"}, "b": [{"c": "foo"}, {"c": "bar"}]}
    result = to_query(data)
    assert unquote(result) == "a[aa]=bar&a[ab]=foo&b[0][c]=foo&b[1][c]=bar"

def test_ai_meta_parameters():
    flayyer = FlayyerAI(
        project="project",
        path="/path/to/product",
        variables={"title": "title"},
        meta=FlayyerMeta(
            agent="whatsapp",
            v="123123",
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/_\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_ua=whatsapp&_w=100&title=title\/path\/to\/product", href) != None

def test_ai_encode_url_happy_path():
    flayyer = FlayyerAI(
        project="project",
        path="/path/to/product",
        variables={"title": "Hello world!"},
        meta=FlayyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/_\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_w=100&title=Hello\+world%21\/path\/to\/product", href) != None

def test_ai_encode_url_default_values():
    flayyer = FlayyerAI(
        project="project",
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/_\/__v=\d+\/", href) != None

def test_ai_encode_url_with_path_missing_slash_at_start():
    flayyer = FlayyerAI(
        project="project",
        path="path/to/product",
        variables={"title": "Hello world!"},
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/_\/__v=\d+&title=Hello\+world%21\/path\/to\/product", href) != None

def test_ai_encode_url_with_signature_hmac():
    flayyer = FlayyerAI(
        project="project",
        path="/collections/col",
        secret="sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx",
        strategy="HMAC",
        meta=FlayyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/e8771c307e66652f\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_w=100\/collections\/col\/?", href) != None

def test_ai_encode_url_with_signature_jwt():
    flayyer = FlayyerAI(
        project="project",
        path="/collections/col",
        secret="sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx",
        strategy="JWT",
        meta=FlayyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flayyer.href()
    assert match("https:\/\/flayyer.ai\/v2\/project\/jwt-eyJhbGciOiJIUzI1NiJ9.eyJpZCI6ImRldiBmb3Jnb3QgdG8gc2x1Z2lmeSIsIndpZHRoIjoiMTAwIiwiaGVpZ2h0IjoyMDB9.0KpbuqbwJyNVNqPOJO_LzvqOXCQK51_WbGEm3pFyY9s\/?\?__v=\d+", href) != None
