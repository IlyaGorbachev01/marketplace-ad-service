from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.exceptions import AdAlreadyArchivedError, InvalidAdError


class AdStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass
class Ad:
    id: int
    user_id: int
    title: str
    description: str
    price: int
    category: str
    city: str
    status: AdStatus
    views: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        _validate_fields(
            title=self.title,
            description=self.description,
            price=self.price,
            category=self.category,
            city=self.city,
        )

    def edit(
        self,
        title: str,
        description: str,
        price: int,
        category: str,
        city: str,
    ) -> None:
        if self.status == AdStatus.ARCHIVED:
            raise AdAlreadyArchivedError
        _validate_fields(
            title=title,
            description=description,
            price=price,
            category=category,
            city=city,
        )
        self.title = title
        self.description = description
        self.price = price
        self.category = category
        self.city = city
        self.updated_at = datetime.now(UTC)

    def archive(self) -> None:
        if self.status == AdStatus.ARCHIVED:
            raise AdAlreadyArchivedError
        self.status = AdStatus.ARCHIVED
        self.updated_at = datetime.now(UTC)

    def increment_views(self) -> None:
        if self.status == AdStatus.ARCHIVED:
            raise AdAlreadyArchivedError
        self.views += 1


def _validate_fields(
    *,
    title: str,
    description: str,
    price: int,
    category: str,
    city: str,
) -> None:
    if not title.strip():
        raise InvalidAdError("title must not be empty")
    if not description.strip():
        raise InvalidAdError("description must not be empty")
    if price < 0:
        raise InvalidAdError("price must be non-negative")
    if not category.strip():
        raise InvalidAdError("category must not be empty")
    if not city.strip():
        raise InvalidAdError("city must not be empty")
