import logging
import os
from datetime import datetime

from fastapi import HTTPException, UploadFile
from starlette import status
from starlette.responses import FileResponse

from app.core.config import configs


class MediaService:

    def __init__(
        self,
        logger: logging.Logger,
    ):
        self.logger = logger

    async def upload_file(self, file: UploadFile):
        if file.filename is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required")

        data_chunk = await file.read()
        if file.size and file.size > configs.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size is too large",
            )
        filename, file_extension = os.path.splitext(file.filename.replace(" ", "_"))
        filename = f"{filename}_{str(round(datetime.utcnow().timestamp() * 1000))}{file_extension}"
        try:
            # check if media folder exists
            if not os.path.exists("./media"):
                os.makedirs("./media")
            with open(f"./media/{filename}", "wb") as f:
                f.write(data_chunk)

        except Exception as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file",
            )

        return filename

    async def delete_file(self, file_name: str):
        try:
            os.remove(f"./media/{file_name}")

        except Exception as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file",
            )

    async def download_file(self, file_name: str):
        try:
            return FileResponse(f"./media/{file_name}")
        except Exception as e:
            self.logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download file",
            )
