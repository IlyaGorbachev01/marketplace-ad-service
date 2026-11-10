from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import (
    CreateAdPort,
    DeleteAdPort,
    GetAdInternalPort,
    GetAdPort,
    IncrementAdViewsPort,
    ListAdsPort,
    UpdateAdPort,
)
from src.application.ports.user_profile import UserProfileService
from src.application.usecases.create_ad import CreateAd
from src.application.usecases.delete_ad import DeleteAd
from src.application.usecases.get_ad import GetAd
from src.application.usecases.get_ad_internal import GetAdInternal
from src.application.usecases.increment_ad_views import IncrementAdViews
from src.application.usecases.list_ads import ListAds
from src.application.usecases.update_ad import UpdateAd
from src.infrastructure.persistence.uow import SQLAlchemyUnitOfWork
from src.settings import Settings

_settings: Settings | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None
_user_profile_service: UserProfileService | None = None


def setup(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
    user_profile_service: UserProfileService,
) -> None:
    global _settings, _session_factory, _user_profile_service
    _settings = settings
    _session_factory = session_factory
    _user_profile_service = user_profile_service


def get_settings() -> Settings:
    assert _settings is not None
    return _settings


def get_uow() -> UnitOfWork:
    assert _session_factory is not None
    return SQLAlchemyUnitOfWork(_session_factory)


def get_user_profile_service() -> UserProfileService:
    assert _user_profile_service is not None
    return _user_profile_service


bearer_scheme = HTTPBearer()


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    settings: "SettingsDep",
) -> int:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload["user_id"]


SettingsDep = Annotated[Settings, Depends(get_settings)]
UowDep = Annotated[UnitOfWork, Depends(get_uow)]
CurrentUserIdDep = Annotated[int, Depends(get_current_user_id)]
UserProfileServiceDep = Annotated[UserProfileService, Depends(get_user_profile_service)]


def get_create_ad(
    uow: UowDep,
) -> CreateAdPort:
    return CreateAd(uow)


def get_update_ad(
    uow: UowDep,
) -> UpdateAdPort:
    return UpdateAd(uow)


def get_delete_ad(
    uow: UowDep,
) -> DeleteAdPort:
    return DeleteAd(uow)


def get_get_ad(
    uow: UowDep,
    user_profile: UserProfileServiceDep,
) -> GetAdPort:
    return GetAd(uow, user_profile)


def get_get_ad_internal(
    uow: UowDep,
) -> GetAdInternalPort:
    return GetAdInternal(uow)


def get_increment_ad_views(
    uow: UowDep,
) -> IncrementAdViewsPort:
    return IncrementAdViews(uow)


def get_list_ads(
    uow: UowDep,
    user_profile: UserProfileServiceDep,
) -> ListAdsPort:
    return ListAds(uow, user_profile)


CreateAdDep = Annotated[CreateAdPort, Depends(get_create_ad)]
UpdateAdDep = Annotated[UpdateAdPort, Depends(get_update_ad)]
DeleteAdDep = Annotated[DeleteAdPort, Depends(get_delete_ad)]
GetAdDep = Annotated[GetAdPort, Depends(get_get_ad)]
GetAdInternalDep = Annotated[GetAdInternalPort, Depends(get_get_ad_internal)]
IncrementAdViewsDep = Annotated[IncrementAdViewsPort, Depends(get_increment_ad_views)]
ListAdsDep = Annotated[ListAdsPort, Depends(get_list_ads)]
