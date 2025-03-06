# crumbles
A simple library for class based view breadcrumbs for any python web framework.

[![CI](https://github.com/maerteijn/crumbles/actions/workflows/ci.yml/badge.svg)](https://github.com/maerteijn/crumbles/actions/workflows/ci.yml)
![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![PyPI version](https://badge.fury.io/py/crumbles.svg?dummy=unused)
![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
![No Dependencies](https://img.shields.io/badge/no%20dependencies-orange)

## Usage

First define a specific mixin for your framework. For example Django:
```python
from django.urls import reverse


class DjangoCrumblesViewMixin(CrumblesViewMixin):
    def url_resolve(self, *args, **kwargs):
        return reverse(*args, **kwargs)
```


Use the Mixin in your View classes and define the breadcrumbs:
```python
class MyListView(View, DjangoCrumblesViewMixin):
    crumbles = (
        CrumbleDefinition(url_name="my-list-view", title="Home"),
    )
```

Add a default breadcrumb to the mixin like so:
```python
class DjangoCrumblesViewMixin(CrumblesViewMixin):
    def __init__(self):
        self.crumbles = (
            CrumbleDefinition(url_name="index", title="Home"),
        ) + type(self).crumbles

    def url_resolve(self, *args, **kwargs):
        return reverse(*args, **kwargs)

```



You can reuse "parent" crumbles for detail pages and use a callable for
url resolve arguments or for defining the title:
```python
from operator import attrgetter, methodcaller


class MyDetailView(View, DjangoCrumblesViewMixin):
    crumbles = MyListView.crumbles + (
        CrumbleDefinition(
            url_name="my-detail-view",
            url_resolve_kwargs={"pk": attrgetter("pk")},
            title=methodcaller("__str__"),
        ),
    )

```

The attributes context will be retrieved from `instance.object`. If this is not available it
will default to the View class instance itself. You can set a custom context variable
(including dotted syntakt) by using `crumbles_context_attribute`:

```python
class MyDetailView(View, DjangoCrumblesViewMixin):
    crumbles_context_attribute = "my_object.parent"
    ...
```

Rendering the breadcrumb should be done in a template. An example for Django (with bootstrap):
```jinja2
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        {% for item in view.resolve_crumbles %}
            {% if forloop.last %}
                <li class="breadcrumb-item active" aria-current="page">{{ item.title }}</li>
            {% else %}
                <li class="breadcrumb-item">
                    {% if item.url %}
                        <a href="{{ item.url }}">{{ item.title}}</a>
                    {% else %}
                        {{ item.title }}
                    {% endif %}
                </li>
            {% endif %}
        {% endfor %}
    </ol>
</nav>
```

## Development setup

### First clone this repository
```
git clone https://github.com/maerteijn/crumbles.git
```

### Install the python project
```bash
pyenv virtualenv crumbles  # or your alternative to create a venv
pyenv activate crumbles
make install
```

### Linting
`ruff` and `mypy` are installed and configured
```bash
make lint
```

### Formatting

`ruff` are configured
```bash
make format
```

### Test

Pytest with coverage is default enabled
```bash
make cov
```
