# flayyer-python

![PyPI - Version](https://img.shields.io/pypi/v/flayyer) ![PyPI - Downloads](https://img.shields.io/pypi/dm/flayyer)

The AI-powered preview system built from your website (no effort required).

![Flayyer live image](https://github.com/flayyer/create-flayyer-app/blob/master/.github/assets/website-to-preview.png?raw=true&v=1)

**This module is agnostic to any Python framework.**

## Index

- [Get started (5 minutes)](#get-started-5-minutes)
- [Advanced usage](#advanced-usage)
- [Flayyer.io](#flayyerio)
- [Development](#development)
- [Test](#test)

## Get started (5 minutes)

Haven't registered your website yet? Go to [Flayyer.com](https://flayyer.com?ref=flayyer-python) and create a project (e.g. `website-com`).

### 1. Install the library

This module requires Python >= 3.6.

Install it with [Poetry](https://python-poetry.org/).

```sh
poetry add flayyer
```

Or install it with [pip](https://pip.pypa.io/en/stable/).

```sh
pip install flayyer
```

### 2. Get your Flayyer.ai smart image link

In your website code (e.g. your landing or product/post view file), set the following:

```python
from flayyer import FlayyerAI

flayyer = FlayyerAI(
  # Your project slug
  project="website-com",
  # The current path of your website
  path="/path/to/product", # In Django you can use {{ request.get_full_path }}
)

# Check:
print(flayyer.href())
# > https://flayyer.ai/v2/website-com/_/__v=1618281823/path/to/product
```

### 3. Put your smart image link in your `<head>` tags

You'll get the best results like this:

```python
<meta property="og:image" content="{{ flayyer.href() }}">
<meta name="twitter:image" content="{{ flayyer.href() }}">
<meta name="twitter:card" content="summary_large_image">
```

### 4. Create a `rule` for your project

Login at [Flayyer.com](https://flayyer.com?ref=flayyer-python) > Go to your Dashboard > Manage rules and create a rule like the following:

[![Flayyer basic rule example](https://github.com/flayyer/create-flayyer-app/blob/master/.github/assets/rule-example.png?raw=true&v=1)](https://flayyer.com/dashboard)

Voilà!

## Advanced usage

Advanced features include:

- Custom variables: additional information for your preview that is not present in your website. [Note: if you need customization you should take a look at [Flayyer.io](#flayyerio)]
- Custom metadata: set custom width, height, resolution, and more (see example).
- Signed URLs.

Here you have a detailed full example for project `website-com` and path `/path/to/product`.

```python
from flayyer import FlayyerAI, FlayyerMeta

flayyer = FlayyerAI(
  # [Required] Your project slug, find it in your dashboard https://flayyer.com/dashboard/.
  project="website-com",
  # [Recommended] The current path of your website (by default it's `/`).
  path="/path/to/product",
  # [Optional] In case you want to provide information that is not present in your page set it here.
  variables={
    "title": "Product name",
    "img": "https://flayyer.com/img/marketplace/flayyer-banner.png",
  },
  # [Optional] Custom metadata for rendering the image. ID is recommended so we provide you with better statistics.
  meta=FlayyerMeta(
    id="jeans-123", # recommended for better stats
    v="12369420123", # specific handler version, by default it's a random number to circumvent platforms' cache,
    width=1200,
    height=600,
    resolution=0.9, # from 0.0 to 1.0
    agent="whatsapp", # force dimensions for specific platform
  ),
)

# Check:
print(flayyer.href())
# > https://flayyer.ai/v2/website-com/_/__v=1618281823/path/to/product
```

For signed URLs, just provide your secret (find it in Dashboard > Project > Advanced settings) and choose a strategy (`HMAC` or `JWT`).

```python
flayyer = FlayyerAI(
  project="website-com",
  path="/path/to/product",
  secret="your-secret-key",
  strategy="JWT", # or 'HMAC'
)

print(flayyer.href())
# > https://flayyer.ai/v2/website-com/jwt-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJhbXMiOnsiX19pZCI6ImplYW5zLTEyMyJ9LCJwYXRoIjoiXC9wYXRoXC90b1wvcHJvZHVjdCJ9.X8Vs5SGEA1-3M6bH-h24jhQnbwH95V_G0f-gPhTBTzE?__v=1618283086
```

## Flayyer.io

As you probably realized, Flayyer.ai uses the [rules defined on your dashboard](https://flayyer.com/dashboard/_/projects) to decide how to handle every image based on path patterns. It fetches and analyse your website for obtaining information and then rendering a content-rich image increasing the click-through-rate with no effort. Let's say _"FlayyerAI render images based on the content of this route"_.

Flayyer.io instead requires you to explicitly declare template and variables for the images to render, **giving you more control for customization**. Let's say _"FlayyerIO render an image using this template and these explicit variables"_.

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

Deploy with:

```sh
# Set API Token
poetry config pypi-token.pypi pypi-TOKEN

poetry version X.Y.Z
poetry build
poetry publish
```

## Test

Run tests with pytest:

```sh
poetry run pytest
```

Run [black](https://github.com/psf/black) linter:

```sh
black .
```
