from urllib.parse import unquote
from re import search, match
import jwt

from flyyer import __version__, FlyyerMeta, to_query, Flyyer, FlyyerRender


def test_version():
    assert __version__ is not None


def test_simple_stringify():
    data = {"a": "hello", "b": 100, "c": False, "d": None, "b": 999}
    result = to_query(data)
    assert result == "a=hello&b=999&c=false"


def test_complex_stringify():
    data = {"a": {"aa": "bar", "ab": "foo"}, "b": [{"c": "foo"}, {"c": "bar"}]}
    result = to_query(data)
    assert unquote(result) == "a[aa]=bar&a[ab]=foo&b[0][c]=foo&b[1][c]=bar"


def test_flyyer_render_url_encoding():
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        variables={"title": "Hello world!"},
    )
    href = flyyer.href()
    assert href.startswith("https://cdn.flyyer.io/render/v2/tenant/deck/template?__v=")
    assert href.endswith("&title=Hello+world%21")
    assert href == str(flyyer)


def test_flyyer_render_url_encoding_with_extension():
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        extension="jpeg",
        variables={"title": "Hello world!"},
    )
    href = flyyer.href()
    assert href.startswith(
        "https://cdn.flyyer.io/render/v2/tenant/deck/template.jpeg?__v="
    )
    assert href.endswith("&title=Hello+world%21")
    assert href == str(flyyer)


def test_flyyer_render_url_encoding_with_version():
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        extension="png",
        version=12,
        variables={"title": "Hello world!"},
    )
    href = flyyer.href()
    assert href.startswith(
        "https://cdn.flyyer.io/render/v2/tenant/deck/template.12.png?__v="
    )
    assert href.endswith("&title=Hello+world%21")
    assert href == str(flyyer)


def test_flyyer_render_meta_parameters():
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        extension="jpeg",
        variables={"title": "title"},
        meta=FlyyerMeta(
            agent="whatsapp",
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    assert href.startswith(
        "https://cdn.flyyer.io/render/v2/tenant/deck/template.jpeg?__v="
    )
    assert href.find("&title=title") != -1
    assert href.find("&_ua=whatsapp") != -1
    assert href.find("&_w=100") != -1
    assert href.find("&_h=200") != -1
    assert href.find("&__id=dev+forgot+to+slugify") != -1
    assert href.find("&_res=") == -1


def test_flyyer_render_encode_url_with_hmac():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        extension="jpeg",
        variables={"title": "Hello world!"},
        secret=key,
        strategy="HMAC",
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/render\/v2\/tenant\/deck\/template.jpeg\?__v=\d+&title=Hello\+world%21&__hmac=6b631ae8c4ca2977",
            href,
        )
        != None
    )


def test_flyyer_render_encode_url_with_jwt_default_values():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        version=4,
        extension="jpeg",
        variables={"title": "Hello world!"},
        secret=key,
        strategy="JWT",
    )
    href = flyyer.href()
    token = search(r"(.*)(jwt=)(.*)", href).groups(2)[2]
    decoded = jwt.decode(token, key, algorithms=["HS256"])
    check = {
        "d": "deck",
        "t": "template",
        "v": 4,
        "e": "jpeg",
        "i": None,
        "w": None,
        "h": None,
        "r": None,
        "u": None,
        "var": {
            "title": "Hello world!",
        }
    }
    assert decoded == check
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/render\/v2\/tenant\?__v=\d+&__jwt=.*",
            href,
        )
        != None
    )


def test_flyyer_render_encode_url_with_jwt_with_meta():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = FlyyerRender(
        tenant="tenant",
        deck="deck",
        template="template",
        secret=key,
        strategy="JWT",
        meta=FlyyerMeta(
            agent="whatsapp",
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    token = search(r"(.*)(jwt=)(.*)", href).groups(2)[2]
    decoded = jwt.decode(token, key, algorithms=["HS256"])
    check = {
        "d": "deck",
        "t": "template",
        "v": None,
        "e": None,
        "i": "dev forgot to slugify",
        "w": "100",
        "h": 200,
        "r": None,
        "u": "whatsapp",
    }
    assert decoded == check
    # assert decoded == check


def test_flyyer_meta_parameters():
    flyyer = Flyyer(
        project="project",
        path="/path/to/product",
        variables={"title": "title"},
        meta=FlyyerMeta(
            agent="whatsapp",
            v="123123",
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/v2\/project\/_\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_ua=whatsapp&_w=100&title=title\/path\/to\/product",
            href,
        )
        != None
    )


def test_flyyer_encode_url_happy_path():
    flyyer = Flyyer(
        project="project",
        path="/path/to/product",
        variables={"title": "Hello world!"},
        meta=FlyyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/v2\/project\/_\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_w=100&title=Hello\+world%21\/path\/to\/product",
            href,
        )
        != None
    )


def test_flyyer_encode_url_default_values():
    flyyer = Flyyer(
        project="project",
    )
    href = flyyer.href()
    assert match(r"https:\/\/cdn.flyyer.io\/v2\/project\/_\/__v=\d+\/", href) != None


def test_flyyer_encode_url_with_path_missing_slash_at_start():
    flyyer = Flyyer(
        project="project",
        path="path/to/product",
        variables={"title": "Hello world!"},
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/v2\/project\/_\/__v=\d+&title=Hello\+world%21\/path\/to\/product",
            href,
        )
        != None
    )


def test_flyyer_encode_url_with_query_params():
    flyyer = Flyyer(
        project="project",
        path="/collection/col?sort=price",
        variables={"title": "Hello world!"},
        meta=FlyyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/v2\/project\/_\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_w=100&title=Hello\+world%21\/collection\/col\/?\?sort=price",
            href,
        )
        != None
    )


def test_flyyer_encode_url_with_hmac():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = Flyyer(
        project="project",
        path="/collections/col",
        secret=key,
        strategy="HMAC",
        meta=FlyyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
        variables={"title": "Hello world!"},
    )
    href = flyyer.href()
    assert (
        match(
            r"https:\/\/cdn.flyyer.io\/v2\/project\/361b2a456daf8415\/__id=dev\+forgot\+to\+slugify&__v=\d+&_h=200&_w=100&title=Hello\+world%21\/collections\/col",
            href,
        )
        != None
    )


def test_flyyer_encode_url_with_jwt_default_values():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = Flyyer(
        project="project",
        secret=key,
        strategy="JWT",
    )
    href = flyyer.href()
    token = search(r"(.*)(jwt-)(.*)(\?__v=\d+)", href).groups(2)[2]
    decoded = jwt.decode(token, key, algorithms=["HS256"])
    params = {k: v for k, v in flyyer.params_hash(True).items() if v is not None}
    check = {"params": params, "path": flyyer.path}
    assert decoded == check


def test_flyyer_encode_url_with_jwt_with_meta():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = Flyyer(
        project="project",
        secret=key,
        strategy="JWT",
        meta=FlyyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    token = search(r"(.*)(jwt-)(.*)(\?__v=\d+)", href).groups(2)[2]
    decoded = jwt.decode(token, key, algorithms=["HS256"])
    params = {k: v for k, v in flyyer.params_hash(True).items() if v is not None}
    check = {"params": params, "path": flyyer.path}
    assert check["params"]["__id"] == "dev forgot to slugify"
    assert decoded == check


def test_flyyer_encode_url_with_jwt_without_slash_at_start():
    key = "sg1j0HVy9bsMihJqa8Qwu8ZYgCYHG0tx"
    flyyer = Flyyer(
        project="project",
        secret=key,
        strategy="JWT",
        path="collections/col",
        meta=FlyyerMeta(
            id="dev forgot to slugify",
            width="100",
            height=200,
        ),
    )
    href = flyyer.href()
    token = search(r"(.*)(jwt-)(.*)(\?__v=\d+)", href).groups(2)[2]
    decoded = jwt.decode(token, key, algorithms=["HS256"])
    params = {k: v for k, v in flyyer.params_hash(True).items() if v is not None}
    check = {"params": params, "path": flyyer.path}
    assert check["params"]["__id"] == "dev forgot to slugify"
    assert check["path"] == "/collections/col"
    assert decoded == check
