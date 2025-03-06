from operator import attrgetter, methodcaller

from crumbles import CrumbleDefinition, CrumbleItem, CrumblesViewMixin

urls = {
    "index": "/",
    "fake-object-list": "/fake-objects",
    "fake-object-detail": "/fake-objects/{pk}",
}


def fake_resolve(name: str, *args, **kwargs) -> str:
    url = urls.get(name)
    return url.format(**kwargs.get("kwargs", {}))


class MyCrumblesViewMixin(CrumblesViewMixin):
    def __init__(self):
        self.crumbles = (CrumbleDefinition(url_name="index", title="Home"),) + type(
            self
        ).crumbles  # prepend a default crumble here

    def url_resolve(self, name: str, *args, **kwargs):
        return fake_resolve(name, *args, **kwargs)


class FakeObjectBase:
    def __init__(self, pk, *args, **kwargs):
        self.pk = pk

    def __str__(self):
        return f"{self.pk}"


class FakeObjectParent(FakeObjectBase):
    pass


class FakeObjectChild(FakeObjectBase):
    def __init__(self, pk, parent, *args, **kwargs):
        super().__init__(pk, *args, **kwargs)
        self.parent = parent


class MyCrumbleView(MyCrumblesViewMixin):
    pass


class MyParentCrumbleView(MyCrumblesViewMixin):
    crumbles = (
        CrumbleDefinition(
            url_name="fake-object-list",
            title="Fake Objects",
        ),
        CrumbleDefinition(
            url_name="fake-object-detail",
            url_resolve_kwargs={"pk": attrgetter("pk")},
            title=methodcaller("__str__"),
        ),
    )

    def __init__(self, pk):
        super().__init__()
        self.object = FakeObjectParent(pk=pk)


class MyChildCrumbleView(MyCrumblesViewMixin):
    crumbles_context_attribute = "object.parent"
    crumbles = MyParentCrumbleView.crumbles + (
        CrumbleDefinition(
            url_name="fake-object-detail",
            url_resolve_kwargs={"pk": attrgetter("pk")},
            title=methodcaller("__str__"),
            context_attribute="object",
        ),
    )

    def __init__(self, pk, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = FakeObjectChild(pk=pk, parent=parent)


def test_crumble_view_mixin__default():
    view_instance = MyCrumbleView()
    crumbles = list(view_instance.resolve_crumbles())

    assert crumbles == [CrumbleItem(url="/", title="Home")]


def test_parent_crumble_view_mixin__with_reversable_urls():
    pk = 1
    view_instance = MyParentCrumbleView(pk=pk)
    crumbles = list(view_instance.resolve_crumbles())

    assert len(crumbles) == 3

    assert crumbles[0] == CrumbleItem(url="/", title="Home")
    assert crumbles[1] == CrumbleItem(
        url=fake_resolve("fake-object-list"),
        title="Fake Objects",
    )
    assert crumbles[2] == CrumbleItem(
        url=fake_resolve("fake-object-detail", kwargs={"pk": pk}), title=str(pk)
    )


def test_parents_crumble_view_mixin__with_reversable_urls():
    pk = 1
    view_instance = MyParentCrumbleView(pk=pk)
    crumbles = list(view_instance.resolve_crumbles())

    assert len(crumbles) == 3

    assert crumbles[0] == CrumbleItem(url="/", title="Home")
    assert crumbles[1] == CrumbleItem(
        url=fake_resolve("fake-object-list"),
        title="Fake Objects",
    )
    assert crumbles[2] == CrumbleItem(
        url=fake_resolve("fake-object-detail", kwargs={"pk": pk}), title=str(pk)
    )


def test_child_crumble_view_mixin__with_reversable_urls_and_context():
    parent_pk = 1
    child_pk = 2

    view_instance = MyChildCrumbleView(
        pk=child_pk, parent=FakeObjectParent(pk=parent_pk)
    )
    crumbles = list(view_instance.resolve_crumbles())

    assert len(crumbles) == 4

    assert crumbles[0] == CrumbleItem(url="/", title="Home")
    assert crumbles[1] == CrumbleItem(
        url=fake_resolve("fake-object-list"),
        title="Fake Objects",
    )
    assert crumbles[2] == CrumbleItem(
        url=fake_resolve("fake-object-detail", kwargs={"pk": parent_pk}),
        title=str(parent_pk),
    )
    assert crumbles[3] == CrumbleItem(
        url=fake_resolve("fake-object-detail", kwargs={"pk": child_pk}),
        title=str(child_pk),
    )
