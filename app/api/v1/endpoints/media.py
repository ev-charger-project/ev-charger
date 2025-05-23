from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, UploadFile

from app.core.container import Container
from app.services import MediaService

router = APIRouter(
    prefix="/media",
    tags=["media"],
)


@router.post(
    "",
    status_code=201,
)
@inject
async def upload_file(
    file: UploadFile,
    media_service: MediaService = Depends(Provide[Container.media_service]),
) -> str:
    return await media_service.upload_file(file)


@router.delete(
    "/{file_name}",
    status_code=202,
)
@inject
async def delete_file(
    file_name: str = Path(..., nullable=False),
    media_service: MediaService = Depends(Provide[Container.media_service]),
):
    return await media_service.delete_file(file_name=file_name)


@router.get(
    "/{file_name}",
)
@inject
async def download_file(
    file_name: str = Path(..., nullable=False),
    media_service: MediaService = Depends(Provide[Container.media_service]),
):
    return await media_service.download_file(file_name=file_name)
