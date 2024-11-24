import logging

from fastapi import UploadFile, status

from app.exceptions.custom_exceptions import ApplicationError

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_FILE_SIZE_MB = MAX_FILE_SIZE / (1024 * 1024)


def handle_file_upload(file_to_upload: UploadFile) -> bytes:
    """
    Handles the upload of a file by reading its content and checking its size.

    Args:
        file_to_upload (UploadFile): The file to be uploaded.

    Returns:
        bytes: The content of the uploaded file.

    Raises:
        ApplicationError: If the file size exceeds the allowed limit.
    """
    uploaded_file_data = file_to_upload.file.read()
    file_size = len(uploaded_file_data)
    file_to_upload.file.seek(0)
    if file_size > MAX_FILE_SIZE:
        logger.error("Upload cancelled, max file size exceeded")
        raise ApplicationError(
            detail=f"File size exceeds the allowed limit of {MAX_FILE_SIZE_MB}MB.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return uploaded_file_data
