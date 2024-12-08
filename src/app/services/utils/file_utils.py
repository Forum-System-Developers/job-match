import logging

from fastapi import UploadFile, status

from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 * 1024)


def validate_uploaded_file(uploaded_file: UploadFile) -> None:
    """
    Validates the uploaded file by checking its size against the maximum allowed file size.

    Args:
        uploaded_file (UploadFile): The file uploaded by the user.

    Raises:
        ApplicationError: If the file size exceeds the maximum allowed limit.
    """
    uploaded_file_data = uploaded_file.file.read()
    file_size = len(uploaded_file_data)
    uploaded_file.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        logger.error("Upload cancelled, max file size exceeded")
        raise ApplicationError(
            detail=f"File size exceeds the allowed limit of {MAX_FILE_SIZE_MB}MB.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
