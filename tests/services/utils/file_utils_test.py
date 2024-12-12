import pytest
from fastapi import status

from app.exceptions.custom_exceptions import ApplicationError
from app.services.utils.file_utils import (
    MAX_FILE_SIZE,
    MAX_FILE_SIZE_MB,
    validate_uploaded_cv,
    validate_uploaded_file,
)


def test_validateUploadedFile_raisesError_whenFileSizeExceedsLimit(mocker) -> None:
    # Arrange
    uploaded_file = mocker.Mock()
    uploaded_file.file.read.return_value = b"a" * (MAX_FILE_SIZE + 1)
    uploaded_file.file.seek.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        validate_uploaded_file(uploaded_file=uploaded_file)

    assert exc_info.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc_info.value.data.detail
        == f"File size exceeds the allowed limit of {MAX_FILE_SIZE_MB}MB."
    )
    uploaded_file.file.seek.assert_called_once_with(0)


def test_validateUploadedFile_passes_whenFileSizeIsWithinLimit(mocker) -> None:
    # Arrange
    uploaded_file = mocker.Mock()
    uploaded_file.file.read.return_value = b"a" * MAX_FILE_SIZE
    uploaded_file.file.seek.return_value = None

    # Act
    validate_uploaded_file(uploaded_file=uploaded_file)

    # Assert
    uploaded_file.file.seek.assert_called_once_with(0)


def test_validateUploadedCv_raisesError_whenFileIsNotPDF(mocker) -> None:
    # Arrange
    uploaded_cv = mocker.Mock()
    uploaded_cv.content_type = "application/msword"

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        validate_uploaded_cv(cv=uploaded_cv)

    assert exc_info.value.data.status == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.data.detail == "Only PDF files are allowed."


def test_validateUploadedCv_raisesError_whenFileSizeExceedsLimit(mocker) -> None:
    # Arrange
    uploaded_cv = mocker.Mock()
    uploaded_cv.content_type = "application/pdf"
    uploaded_cv.file.read.return_value = b"a" * (MAX_FILE_SIZE + 1)
    uploaded_cv.file.seek.return_value = None

    # Act & Assert
    with pytest.raises(ApplicationError) as exc_info:
        validate_uploaded_cv(cv=uploaded_cv)

    assert exc_info.value.data.status == status.HTTP_400_BAD_REQUEST
    assert (
        exc_info.value.data.detail
        == f"File size exceeds the allowed limit of {MAX_FILE_SIZE_MB}MB."
    )
    uploaded_cv.file.seek.assert_called_once_with(0)


def test_validateUploadedCvPasses_whenFileIsPDFAndSizeIsWithinLimit(mocker) -> None:
    # Arrange
    uploaded_cv = mocker.Mock()
    uploaded_cv.content_type = "application/pdf"
    uploaded_cv.file.read.return_value = b"a" * MAX_FILE_SIZE
    uploaded_cv.file.seek.return_value = None

    # Act
    validate_uploaded_cv(cv=uploaded_cv)

    # Assert
    uploaded_cv.file.seek.assert_called_once_with(0)
