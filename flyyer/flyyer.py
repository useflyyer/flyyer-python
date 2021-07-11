from time import time
from urllib.parse import urlencode
from typing import Optional, Mapping, Union, Any
from typing_extensions import TypedDict
from hashlib import sha256
import hmac
import jwt


class FlyyerMeta(TypedDict, total=False):
    agent: str
    width: Union[str, int]
    height: Union[str, int]
    resolution: Union[str, int]
    id: Union[str, int]
    v: Union[str, int]


class FlyyerRender:
    def __init__(
        self,
        tenant: str,
        deck: str,
        template: str,
        version: Optional[int] = None,
        extension: str = "jpeg",
        variables: Optional[Mapping[Any, Any]] = None,
        meta: Optional[FlyyerMeta] = None,
    ):
        self.tenant = tenant
        self.deck = deck
        self.template = template
        self.version = version
        self.extension = extension
        self.variables = variables if variables else {}
        self.meta = meta if meta else {}

    def querystring(self) -> str:
        defaults = {
            "__v": self.meta.get(
                "v", str(int(time()))
            ),  # This forces crawlers to refresh the image
            "__id": self.meta.get("id"),
            "_w": self.meta.get("width"),
            "_h": self.meta.get("height"),
            "_res": self.meta.get("resolution"),
            "_ua": self.meta.get("agent"),
        }
        return to_query({**defaults, **self.variables})

    def href(self) -> str:
        query = self.querystring()
        if self.version:
            return f"https://cdn.flyyer.io/render/v2/{self.tenant}/{self.deck}/{self.template}.{self.version}.{self.extension}?{query}"
        return f"https://cdn.flyyer.io/render/v2/{self.tenant}/{self.deck}/{self.template}.{self.extension}?{query}"

    def __str__(self):
        return self.href()


class Flyyer:
    def __init__(
        self,
        project: str,
        path: Optional[str] = "/",
        secret: Optional[str] = None,
        strategy: Optional[str] = None,
        variables: Optional[Mapping[Any, Any]] = None,
        meta: Optional[FlyyerMeta] = None,
    ):
        self.project = project
        self.path = path if path.startswith("/") else "/" + path
        self.secret = secret
        self.strategy = strategy
        self.variables = variables if variables else {}
        self.meta = meta if meta else {}
        if strategy and strategy.lower() != "hmac" and strategy.lower() != "jwt":
            raise Exception("Invalid `strategy`. Valid options are `HMAC` or `JWT`.")
        if strategy and not secret:
            raise Exception(
                "Missing `secret`. You can find it in your project in Advanced settings."
            )
        if secret and not strategy:
            raise Exception(
                "Got `secret` but missing `strategy`. Valid options are `HMAC` or `JWT`."
            )

    def params_hash(self, ignoreV) -> str:
        defaults = {
            "__v": self.meta.get(
                "v", str(int(time()))
            ),  # This forces crawlers to refresh the image
            "__id": self.meta.get("id"),
            "_w": self.meta.get("width"),
            "_h": self.meta.get("height"),
            "_res": self.meta.get("resolution"),
            "_ua": self.meta.get("agent"),
        }
        if ignoreV:
            defaults.pop("__v", None)
        return {**defaults, **self.variables}

    def querystring(self, ignoreV=False) -> str:
        params = self.params_hash(ignoreV)
        aux = to_query(params).split("&")
        aux.sort()
        return "&".join(aux)

    def sign(self) -> str:
        # strategy & secret consistency checked on init
        if self.strategy == None:
            return "_"
        key = self.secret.encode("ASCII")
        if self.strategy and self.strategy.lower() == "hmac":
            data = (self.project + self.path + self.querystring(True)).encode("ASCII")
            return hmac.new(key, data, sha256).hexdigest()[:16]
        elif self.strategy and self.strategy.lower() == "jwt":
            params = {k: v for k, v in self.params_hash(True).items() if v is not None}
            data = {"params": params, "path": self.path}
            return jwt.encode(data, key, algorithm="HS256", headers=None)

    def href(self) -> str:
        query = self.querystring()
        signature = self.sign()
        if self.strategy and self.strategy.lower() == "jwt":
            final_version = self.meta.get("v", str(int(time())))
            return f"https://cdn.flyyer.io/v2/{self.project}/jwt-{signature}?__v={final_version}"
        else:
            return (
                f"https://cdn.flyyer.io/v2/{self.project}/{signature}/{query}{self.path}"
            )

    def __str__(self):
        return self.href()


# From https://stackoverflow.com/a/43347067/3416691
# Alternative: https://stackoverflow.com/a/4014164/3416691
def to_query(params: Mapping[Any, Any]) -> str:
    g_encode_params = {}

    def _encode_params(params, p_key=None):
        encode_params = {}
        if params is None:
            pass  # skip
        elif isinstance(params, dict):
            for key in params:
                encode_key = "{}[{}]".format(p_key, key)
                encode_params[encode_key] = params[key]
        elif isinstance(params, (list, tuple)):
            for offset, value in enumerate(params):
                encode_key = "{}[{}]".format(p_key, offset)
                encode_params[encode_key] = value
        elif isinstance(params, (bool)):
            g_encode_params[p_key] = str(params).lower()
        else:
            g_encode_params[p_key] = params

        for key in encode_params:
            value = encode_params[key]
            _encode_params(value, key)

    if isinstance(params, dict):
        for key in params:
            _encode_params(params[key], key)

    return urlencode(g_encode_params)
