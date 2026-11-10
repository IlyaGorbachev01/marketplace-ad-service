import pytest

from src.application.exceptions import AdNotFoundError
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.delete_ad import DeleteAd
from src.application.usecases.increment_ad_views import IncrementAdViews
from tests.conftest import FakeUnitOfWork


async def _create_ad(fake_uow: FakeUnitOfWork) -> int:
    ad = await CreateAd(fake_uow).execute(
        user_id=1,
        title="T",
        description="d",
        price=100,
        category="c",
        city="x",
    )
    return ad.id


@pytest.mark.asyncio
async def test_increment_ad_views(fake_uow: FakeUnitOfWork) -> None:
    ad_id = await _create_ad(fake_uow)
    usecase = IncrementAdViews(fake_uow)

    ad = await usecase.execute(ad_id)

    assert ad.views == 1
    assert fake_uow.committed

    ad = await usecase.execute(ad_id)
    assert ad.views == 2


@pytest.mark.asyncio
async def test_increment_ad_views_not_found(fake_uow: FakeUnitOfWork) -> None:
    fake_uow.committed = False
    usecase = IncrementAdViews(fake_uow)

    with pytest.raises(AdNotFoundError):
        await usecase.execute(999)

    assert not fake_uow.committed


@pytest.mark.asyncio
async def test_increment_ad_views_archived(fake_uow: FakeUnitOfWork) -> None:
    ad_id = await _create_ad(fake_uow)
    await DeleteAd(fake_uow).execute(ad_id=ad_id, user_id=1)
    fake_uow.committed = False

    usecase = IncrementAdViews(fake_uow)
    with pytest.raises(AdNotFoundError):
        await usecase.execute(ad_id)

    assert not fake_uow.committed
    archived = await fake_uow.ads.get_by_id(ad_id)
    assert archived is not None
    assert archived.views == 0
