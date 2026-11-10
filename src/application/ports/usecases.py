from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain.entities import Ad


@dataclass(frozen=True)
class AdView:
    ad: Ad
    user_name: str | None


class CreateAdPort(ABC):
    @abstractmethod
    async def execute(
        self,
        user_id: int,
        title: str,
        description: str,
        price: int,
        category: str,
        city: str,
    ) -> Ad: ...


class UpdateAdPort(ABC):
    @abstractmethod
    async def execute(
        self,
        ad_id: int,
        user_id: int,
        title: str | None,
        description: str | None,
        price: int | None,
        category: str | None,
        city: str | None,
    ) -> Ad: ...


class DeleteAdPort(ABC):
    @abstractmethod
    async def execute(
        self,
        ad_id: int,
        user_id: int,
    ) -> None: ...


class GetAdPort(ABC):
    @abstractmethod
    async def execute(
        self,
        ad_id: int,
    ) -> AdView: ...


class IncrementAdViewsPort(ABC):
    @abstractmethod
    async def execute(
        self,
        ad_id: int,
    ) -> Ad: ...


class GetAdInternalPort(ABC):
    @abstractmethod
    async def execute(
        self,
        ad_id: int,
    ) -> Ad: ...


class ListAdsPort(ABC):
    @abstractmethod
    async def execute(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AdView], int]: ...
