# flayyer-python
![PyPI - Version](https://img.shields.io/pypi/v/flayyer)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flayyer)

This module is agnostic to any Python framework and has zero external dependencies.

To create a FLAYYER template please refer to: [flayyer.com](https://flayyer.com?ref=flayyer-python)

## Installation

Install it with [Poetry](https://python-poetry.org/), the modern package manager.

```sh
poetry add flayyer
```

Don’t worry: if poetry is not your thing, you can also use [pip](https://pip.pypa.io/en/stable/).

```sh
pip install flayyer
```

**Note:** This client requires [**Python 3.6+**](https://docs.python.org/3/whatsnew/3.6.html).

## Usage

After installing the package you can format URL as:

```python
from flayyer import Flayyer

flayyer = Flayyer(
    tenant="tenant",
    deck="deck",
    template="template",
    variables={"title": "Hello world!"},
)

# Use this image in your <head/> tags
url = flayyer.href()
# > https://flayyer.io/v2/tenant/deck/template.jpeg?__v=1596906866&title=Hello+world%21
```

Variables can be complex arrays and hashes.

```python
from flayyer import Flayyer, FlayyerMeta

flayyer = Flayyer(
    tenant="tenant",
    deck="deck",
    template="template",
    variables={
        "items": [
            { "text": "Oranges", "count": 12 },
            { "text": "Apples", "count": 14 },
        ],
    },
    meta=FlayyerMeta(
        id="slug-or-id", # To identify the resource in our analytics report
    ),
)
```

**IMPORTANT: variables must be serializable.**

To decode the URL for debugging purposes:

```python
from urllib.parse import unquote

print(unquote(url))
# > https://flayyer.io/v2/tenant/deck/template.jpeg?title=Hello+world!&__v=123
```

## Development

Prepare the local environment:

```sh
poetry install
```

```sh
poetry shell
```

Run tests with pytest:

```sh
pytest
```

Deploy with:

```sh
# Set API Token
poetry config pypi-token.pypi pypi-TOKEN

poetry version X.Y.Z
poetry build
poetry publish
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/flayyer/flayyer-python.

## License

The module is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgements

Heads up to [**@nebil**](https://github.com/nebil) for his advice in the development of this Python module.
