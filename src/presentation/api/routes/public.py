from fastapi import APIRouter, HTTPException, Query, Response, status

from src.application.exceptions import AdNotFoundError, ForbiddenError
from src.presentation.api.dependencies import (
    CreateAdDep,
    CurrentUserIdDep,
    DeleteAdDep,
    GetAdDep,
    IncrementAdViewsDep,
    ListAdsDep,
    UpdateAdDep,
)
from src.presentation.api.schemas import (
    AdListResponse,
    AdResponse,
    CreateAdRequest,
    MyAdsResponse,
    UpdateAdRequest,
)

router = APIRouter(prefix="/ads", tags=["ads"])


@router.get("")
async def list_ads(
    usecase: ListAdsDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> AdListResponse:
    views, total = await usecase.execute(
        user_id=None,
        limit=limit,
        offset=offset,
    )
    return AdListResponse(
        items=[AdResponse.from_view(v) for v in views],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/my")
async def list_my_ads(
    usecase: ListAdsDep,
    current_user_id: CurrentUserIdDep,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> MyAdsResponse:
    views, total = await usecase.execute(
        user_id=current_user_id,
        limit=limit,
        offset=offset,
    )
    return MyAdsResponse(
        items=[AdResponse.from_view(v) for v in views],
        total=total,
    )


@router.get("/{ad_id}")
async def get_ad(
    ad_id: int,
    usecase: GetAdDep,
    increment_views: IncrementAdViewsDep,
) -> AdResponse:
    try:
        await increment_views.execute(ad_id)
        view = await usecase.execute(ad_id)
    except AdNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )
    return AdResponse.from_view(view)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_ad(
    body: CreateAdRequest,
    current_user_id: CurrentUserIdDep,
    usecase: CreateAdDep,
) -> AdResponse:
    ad = await usecase.execute(
        user_id=current_user_id,
        title=body.title,
        description=body.description,
        price=body.price,
        category=body.category,
        city=body.city,
    )
    return AdResponse.from_entity(ad)


@router.put("/{ad_id}")
async def update_ad(
    ad_id: int,
    body: UpdateAdRequest,
    current_user_id: CurrentUserIdDep,
    usecase: UpdateAdDep,
) -> AdResponse:
    try:
        ad = await usecase.execute(
            ad_id=ad_id,
            user_id=current_user_id,
            title=body.title,
            description=body.description,
            price=body.price,
            category=body.category,
            city=body.city,
        )
    except AdNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )
    except ForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return AdResponse.from_entity(ad)


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: int,
    current_user_id: CurrentUserIdDep,
    usecase: DeleteAdDep,
) -> Response:
    try:
        await usecase.execute(ad_id=ad_id, user_id=current_user_id)
    except AdNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found",
        )
    except ForbiddenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
