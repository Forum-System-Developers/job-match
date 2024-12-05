import pytest

from app.schemas.common import MessageResponse
from app.services.mail_service import MailService

SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 465
SMTP_USERNAME = "username"
SMTP_PASSWORD = "password"
SMTP_FROM_EMAIL = "from@example.com"

TO_EMAIL = "toemail@example.com"
SUBJECT = "Test Subject"
MESSAGE = "Test Message"


@pytest.fixture
def mail_service():
    return MailService(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        from_email=SMTP_FROM_EMAIL,
    )


def test_sendMail_returnsSuccessMessage_whenMailIsSentSuccessfully(
    mocker, mail_service
):
    # Arrange
    mock_server = mocker.Mock()
    mock_message = mocker.Mock()
    mock_smtp = mocker.patch("smtplib.SMTP_SSL", autospec=True)
    mock_smtp.return_value.__enter__.return_value = mock_server
    mock_create_message = mocker.patch.object(
        mail_service, "_create_message", return_value=mock_message
    )

    # Act
    response = mail_service.send_mail(
        to_email=TO_EMAIL,
        subject=SUBJECT,
        body=MESSAGE,
    )

    # Assert
    mock_create_message.assert_called_once_with(
        to_email=TO_EMAIL,
        subject=SUBJECT,
        body=MESSAGE,
        list_unsubscribe=None,
    )
    mock_message.as_string.assert_called_once()
    mock_smtp.assert_called_once_with(SMTP_SERVER, SMTP_PORT)
    mock_server.login.assert_called_once_with(SMTP_USERNAME, SMTP_PASSWORD)
    mock_server.sendmail.assert_called_once_with(SMTP_FROM_EMAIL, TO_EMAIL, mocker.ANY)
    assert response == MessageResponse(
        message=f"Message sent successfully to {TO_EMAIL}"
    )


def test_sendMail_returnsErrorMessage_whenMailSendingFails(mocker, mail_service):
    # Arrange
    mock_smtp = mocker.patch("smtplib.SMTP_SSL", autospec=True)
    mock_smtp.side_effect = Exception("Error sending email")
    mock_create_message = mocker.patch.object(
        mail_service, "_create_message", return_value=mocker.Mock()
    )

    # Act
    response = mail_service.send_mail(
        to_email=TO_EMAIL,
        subject=SUBJECT,
        body=MESSAGE,
    )

    # Assert
    mock_create_message.assert_called_once_with(
        to_email=TO_EMAIL,
        subject=SUBJECT,
        body=MESSAGE,
        list_unsubscribe=None,
    )
    mock_smtp.assert_called_once_with(SMTP_SERVER, SMTP_PORT)
    assert response == MessageResponse(message=f"Error sending email to {TO_EMAIL}")
