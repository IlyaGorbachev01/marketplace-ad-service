from datetime import UTC, datetime

import pytest

from src.domain.entities import Ad, AdStatus
from src.domain.exceptions import AdAlreadyArchivedError, InvalidAdError


def _make_ad(**overrides) -> Ad:
    now = datetime.now(UTC)
    defaults = dict(
        id=1,
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
        status=AdStatus.ACTIVE,
        views=0,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    return Ad(**defaults)


def test_construct_rejects_empty_title() -> None:
    with pytest.raises(InvalidAdError):
        _make_ad(title="   ")


def test_construct_rejects_negative_price() -> None:
    with pytest.raises(InvalidAdError):
        _make_ad(price=-1)


def test_edit_updates_fields_and_bumps_updated_at() -> None:
    ad = _make_ad()
    before = ad.updated_at

    ad.edit(
        title="New",
        description="d2",
        price=200,
        category="c2",
        city="x2",
    )

    assert ad.title == "New"
    assert ad.price == 200
    assert ad.updated_at >= before


def test_edit_rejects_invalid_values() -> None:
    ad = _make_ad()
    with pytest.raises(InvalidAdError):
        ad.edit(
            title="t",
            description="d",
            price=-10,
            category="c",
            city="x",
        )


def test_edit_on_archived_raises() -> None:
    ad = _make_ad(status=AdStatus.ARCHIVED)
    with pytest.raises(AdAlreadyArchivedError):
        ad.edit(
            title="t",
            description="d",
            price=100,
            category="c",
            city="x",
        )


def test_archive_sets_status() -> None:
    ad = _make_ad()
    ad.archive()
    assert ad.status == AdStatus.ARCHIVED


def test_archive_already_archived_raises() -> None:
    ad = _make_ad(status=AdStatus.ARCHIVED)
    with pytest.raises(AdAlreadyArchivedError):
        ad.archive()


def test_increment_views_bumps_counter() -> None:
    ad = _make_ad()
    ad.increment_views()
    assert ad.views == 1


def test_increment_views_on_archived_raises() -> None:
    ad = _make_ad(status=AdStatus.ARCHIVED)
    with pytest.raises(AdAlreadyArchivedError):
        ad.increment_views()
