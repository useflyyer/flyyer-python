from time import time
from urllib.parse import urlencode
from typing import Optional, Mapping, Any


class Flayyer:
    def __init__(
        self,
        tenant: str,
        deck: str,
        template: str,
        version: Optional[int] = None,
        extension: str = "jpeg",
        variables: Optional[Mapping[Any, Any]] = None,
    ):
        self.tenant = tenant
        self.deck = deck
        self.template = template
        self.version = version
        self.extension = extension
        self.variables = variables if variables else {}

    @property
    def querystring(self) -> str:
        defaults = {
            "__v": str(int(time())),  # This forces crawlers to refresh the image
        }
        return to_query({**defaults, **self.variables})

    @property
    def href(self) -> str:
        if self.version:
            return f"https://flayyer.host/v2/{self.tenant}/{self.deck}/{self.template}.{self.version}.{self.extension}?{self.querystring}"
        return f"https://flayyer.host/v2/{self.tenant}/{self.deck}/{self.template}.{self.extension}?{self.querystring}"


# From https://stackoverflow.com/a/43347067/3416691
# Alternative: https://stackoverflow.com/a/4014164/3416691
def to_query(params: Mapping[Any, Any]) -> str:
    g_encode_params = {}

    def _encode_params(params, p_key=None):
        encode_params = {}
        if params is None:
            g_encode_params[p_key] = ""  # Empty
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
