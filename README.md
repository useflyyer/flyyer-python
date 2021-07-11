# flyyer-python

![PyPI - Version](https://img.shields.io/pypi/v/flyyer) ![PyPI - Downloads](https://img.shields.io/pypi/dm/flyyer)

The AI-powered preview system built from your website (no effort required).

![Flyyer live image](https://github.com/useflyyer/create-flyyer-app/blob/master/.github/assets/website-to-preview.png?raw=true&v=1)

**This module is agnostic to any Python framework.**

## Index

- [Get started (5 minutes)](#get-started-5-minutes)
- [Advanced usage](#advanced-usage)
- [Flyyer Render](#flyyer-render)
- [Development](#development)
- [Test](#test)

## Get started (5 minutes)

Haven't registered your website yet? Go to [Flyyer.io](https://flyyer.io?ref=flyyer-python) and create a project (e.g. `website-com`).

### 1. Install the library

This module requires Python >= 3.6.

Install it with [Poetry](https://python-poetry.org/).

```sh
poetry add flyyer
```

Or install it with [pip](https://pip.pypa.io/en/stable/).

```sh
pip install flyyer
```

### 2. Get your Flyyer.io smart image link

In your website code (e.g. your landing or product/post view file), set the following:

```python
from flyyer import Flyyer

flyyer = Flyyer(
  # Your project slug
  project="website-com",
  # The current path of your website
  path="/path/to/product", # In Django you can use {{ request.get_full_path }}
)

# Check:
print(flyyer.href())
# > https://cdn.flyyer.io/v2/website-com/_/__v=1618281823/path/to/product
```

### 3. Put your smart image link in your `<head>` tags

You'll get the best results like this:

```python
<meta property="og:image" content="{{ flyyer.href() }}">
<meta name="twitter:image" content="{{ flyyer.href() }}">
<meta name="twitter:card" content="summary_large_image">
```

### 4. Create a `rule` for your project

Go to your dashboard [here](https://flyyer.io/dashboard/_/projects/_/manage) and create a rule like the following:

[![Flyyer basic rule example](https://github.com/useflyyer/create-flyyer-app/blob/master/.github/assets/rule-example.png?raw=true&v=1)](https://flyyer.io/dashboard)

Voilà!

## Advanced usage

Advanced features include:

- Custom variables: additional information for your preview that is not present in your website. [Note: if you need customization you should take a look at [Flyyer Render](#flyyer-render)]
- Custom metadata: set custom width, height, resolution, and more (see example).
- Signed URLs.

Here you have a detailed full example for project `website-com` and path `/path/to/product`.

```python
from flyyer import Flyyer, FlyyerMeta

flyyer = Flyyer(
  # [Required] Your project slug, find it in your dashboard https://www.flyyer.io/dashboard/_/projects/_/integrate.
  project="website-com",
  # [Recommended] The current path of your website (by default it's `/`).
  path="/path/to/product",
  # [Optional] In case you want to provide information that is not present in your page set it here.
  variables={
    "title": "Product name",
    "img": "https://flyyer.io/img/marketplace/flyyer-banner.png",
  },
  # [Optional] Custom metadata for rendering the image. ID is recommended so we provide you with better statistics.
  meta=FlyyerMeta(
    id="jeans-123", # recommended for better stats
    v="12369420123", # specific handler version, by default it's a random number to circumvent platforms' cache,
    width=1200,
    height=600,
    resolution=0.9, # from 0.0 to 1.0
    agent="whatsapp", # force dimensions for specific platform
  ),
)

# Check:
print(flyyer.href())
# > https://cdn.flyyer.io/v2/website-com/_/__v=1618281823/path/to/product
```

For signed URLs, just provide your secret (find it in Dashboard > Project > Advanced settings) and choose a strategy (`HMAC` or `JWT`).

```python
flyyer = Flyyer(
  project="website-com",
  path="/path/to/product",
  secret="your-secret-key",
  strategy="JWT", # or 'HMAC'
)

print(flyyer.href())
# > https://cdn.flyyer.io/v2/website-com/jwt-eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXJhbXMiOnsiX19pZCI6ImplYW5zLTEyMyJ9LCJwYXRoIjoiXC9wYXRoXC90b1wvcHJvZHVjdCJ9.X8Vs5SGEA1-3M6bH-h24jhQnbwH95V_G0f-gPhTBTzE?__v=1618283086
```

## Flyyer Render

As you probably realized, **Flyyer** uses the [rules defined on your dashboard](https://flyyer.io/dashboard/_/projects) to decide how to handle every image based on path patterns. It analyses your website to obtain information and then render a content-rich image with no effort. Let's say _"Flyyer delivers images based on the content of this route"_.

**Flyyer Render** instead requires you to explicitly declare template and variables for the images to render, **giving you more control for customization**. Let's say _"FlyyerRender delivers an image using this template and these explicit variables"_.

```python
from flyyer import FlyyerRender

flyyer = FlyyerRender(
    tenant="tenant",
    deck="deck",
    template="template",
    variables={"title": "Hello world!"},
)

# Use this image in your <head/> tags
url = flyyer.href()
# > https://cdn.flyyer.io/render/v2/tenant/deck/template.jpeg?__v=1596906866&title=Hello+world%21
```

Variables can be complex arrays and hashes.

```python
from flyyer import FlyyerRender, FlyyerMeta

flyyer = FlyyerRender(
    tenant="tenant",
    deck="deck",
    template="template",
    variables={
        "items": [
            { "text": "Oranges", "count": 12 },
            { "text": "Apples", "count": 14 },
        ],
    },
    meta=FlyyerMeta(
        id="slug-or-id", # To identify the resource in our analytics report
    ),
)
```

**IMPORTANT: variables must be serializable.**

To decode the URL for debugging purposes:

```python
from urllib.parse import unquote

print(unquote(url))
# > https://cdn.flyyer.io/render/v2/tenant/deck/template.jpeg?title=Hello+world!&__v=123
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
