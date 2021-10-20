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
        extension: Optional[str] = None,
        variables: Optional[Mapping[Any, Any]] = None,
        meta: Optional[FlyyerMeta] = None,
        secret: Optional[str] = None,
        strategy: Optional[str] = None,
    ):
        self.tenant = tenant
        self.deck = deck
        self.template = template
        self.version = version
        self.extension = extension
        self.variables = variables if variables else {}
        self.meta = meta if meta else {}
        self.secret = secret
        self.strategy = strategy
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

    def querystring(self) -> str:
        default_v = {
            "__v": self.meta.get("v", str(int(time())))
        }  # This forces crawlers to refresh the image
        defaults_without_v = {
            "__id": self.meta.get("id"),
            "_w": self.meta.get("width"),
            "_h": self.meta.get("height"),
            "_res": self.meta.get("resolution"),
            "_ua": self.meta.get("agent"),
        }
        if self.strategy and self.secret:
            key = self.secret.encode("ASCII")
            if self.strategy.lower() == "hmac":
                data = "#".join(
                    [
                        self.deck,
                        self.template,
                        self.version or "",
                        self.extension or "",
                        to_query(
                            {
                                **defaults_without_v,
                                **self.variables,
                            }
                        ),
                    ],
                ).encode("ASCII")
                __hmac = hmac.new(key, data, sha256).hexdigest()[:16]
                return to_query(
                    {
                        **default_v,
                        **defaults_without_v,
                        **self.variables,
                        "__hmac": __hmac,
                    }
                )
            elif self.strategy.lower() == "jwt":
                jwt_defaults = {
                    "i": self.meta.get("id"),
                    "w": self.meta.get("width"),
                    "h": self.meta.get("height"),
                    "r": self.meta.get("resolution"),
                    "u": self.meta.get("agent"),
                    "var": self.variables,
                }
                data = {
                    "d": self.deck,
                    "t": self.template,
                    "v": self.version,
                    "e": self.extension,
                    **jwt_defaults,
                }
                __jwt = jwt.encode(data, key, algorithm="HS256", headers=None)
                return to_query({"__jwt": __jwt, **default_v})
        else:
            return to_query({**default_v, **defaults_without_v, **self.variables})

    def href(self) -> str:
        query = self.querystring()
        base_href = "https://cdn.flyyer.io/render/v2"
        if self.strategy and self.strategy.lower() == "jwt":
            return f"{base_href}/{self.tenant}?{query}"
        final_href = f"{base_href}/{self.tenant}/{self.deck}/{self.template}"
        if self.version:
            final_href += f".{self.version}"
        if self.extension:
            final_href += f".{self.extension}"
        return f"{final_href}?{query}"

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
        default: Optional[str] = None,
    ):
        self.project = project
        self.path = path if path.startswith("/") else "/" + path
        self.default = default
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

    def params_hash(self, ignoreV, isJWT=False) -> Union[str, dict]:
        if not isJWT:
            defaults = {
                "__v": self.meta.get(
                    "v", str(int(time()))
                ),  # This forces crawlers to refresh the image
                "__id": self.meta.get("id"),
                "_w": self.meta.get("width"),
                "_h": self.meta.get("height"),
                "_res": self.meta.get("resolution"),
                "_ua": self.meta.get("agent"),
                "_def": self.default,
            }
            if ignoreV:
                defaults.pop("__v", None)
            return {**defaults, **self.variables}
        else:
            jwt_defaults = {
                "path": self.path,
                "params": {
                    "i": self.meta.get("id"),
                    "w": self.meta.get("width"),
                    "h": self.meta.get("height"),
                    "r": self.meta.get("resolution"),
                    "u": self.meta.get("agent"),
                    "def": self.default,
                    "var": self.variables,
                },
            }
            return jwt_defaults

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
            data = {k: v for k, v in self.params_hash(True, True).items() if v is not None}
            return jwt.encode(data, key, algorithm="HS256", headers=None)

    def href(self) -> str:
        signature = self.sign()
        if self.strategy and self.strategy.lower() == "jwt":
            final_version = self.meta.get("v", str(int(time())))
            return f"https://cdn.flyyer.io/v2/{self.project}/jwt-{signature}?__v={final_version}"
        else:
            query = self.querystring()
            return f"https://cdn.flyyer.io/v2/{self.project}/{signature}/{query}{self.path}"

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
