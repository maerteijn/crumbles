import logging
from abc import abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from operator import attrgetter
from typing import Any, Protocol

logger = logging.getLogger(__name__)


@dataclass
class CrumbleDefinition:
    title: str | Callable
    url_name: str | None = None
    url_resolve_kwargs: dict[str, Callable] = field(default_factory=dict)
    context_attribute: str | None = None


CrumbleDefinitionList = tuple[CrumbleDefinition, ...]


@dataclass
class CrumbleItem:
    title: str
    url: str | None = None


Crumbles = Iterator[CrumbleItem]


class CrumblesViewMixin(Protocol):
    crumbles: CrumbleDefinitionList = tuple()
    crumbles_context_attribute: str | None = "object"

    @property
    def crumbles_context(self) -> Any:
        context_attribute = self.crumbles_context_attribute

        if context_attribute is not None:
            try:
                return attrgetter(context_attribute)(self)
            except AttributeError:
                logger.debug("Can't find {context_attribute} on {self}")

        # Fallback context will be the view itself when the context_attribute
        # can't be found or explicitly set to None
        return self

    def resolve_crumbles(self, context: Any = None) -> Crumbles:
        for crumb in self.crumbles:
            breadcrum_item_kwargs = dict()
            context = context or self.crumbles_context

            # A local override of the context attribute
            if crumb.context_attribute and hasattr(self, crumb.context_attribute):
                context = attrgetter(crumb.context_attribute)(self)

            if callable(crumb.title):
                title = str(crumb.title(context))
            else:
                title = str(crumb.title)

            breadcrum_item_kwargs.update({"title": title})

            if crumb.url_name:
                url_resolve_kwargs = crumb.url_resolve_kwargs

                url = self.url_resolve(
                    crumb.url_name,
                    kwargs={x: y(context) for x, y in url_resolve_kwargs.items()},
                )
                breadcrum_item_kwargs.update({"url": url})

            yield CrumbleItem(**breadcrum_item_kwargs)

    @abstractmethod
    def url_resolve(self, *args: Any, **kwargs: Any) -> str: ...
