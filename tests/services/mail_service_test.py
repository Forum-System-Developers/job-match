from email.mime.multipart import MIMEMultipart

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

MESSAGE_ID = "<msg-id>"
UNSUBSCRIBE_HEADER = f"<mailto:{SMTP_FROM_EMAIL}?subject=unsubscribe>"


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


def test_createMessage_createsMessageWithCorrectFields(mocker, mail_service):
    # Arrange
    mock_make_msgid = mocker.patch(
        "app.services.mail_service.make_msgid", return_value=MESSAGE_ID
    )
    mock_generate_unsubscribe_header = mocker.patch.object(
        mail_service, "_generate_unsubscribe_header", return_value=UNSUBSCRIBE_HEADER
    )

    # Act
    message = mail_service._create_message(
        to_email=TO_EMAIL,
        subject=SUBJECT,
        body=MESSAGE,
    )

    # Assert
    mock_make_msgid.assert_called_once()
    mock_generate_unsubscribe_header.assert_called_once_with(None)
    assert isinstance(message, MIMEMultipart)
    assert message["From"] == SMTP_FROM_EMAIL
    assert message["To"] == TO_EMAIL
    assert message["Subject"] == SUBJECT
    assert isinstance(message["Date"], str)
    assert message.get_payload()[0].get_payload() == MESSAGE
    assert message["Message-ID"] == MESSAGE_ID
    assert message["List-Unsubscribe"] == UNSUBSCRIBE_HEADER


def test_generateUnsubscribeHeader_returnsDefaultHeader_whenNoArgumentsProvided(
    mail_service,
):
    # Arrange & Act
    header = mail_service._generate_unsubscribe_header()

    # Assert
    assert header == UNSUBSCRIBE_HEADER


def test_generateUnsubscribeHeader_returnsCustomHeader_whenCustomHeaderProvided(
    mail_service,
):
    # Arrange
    custom_header = "<http://unsubscribe.example.com>"

    # Act
    header = mail_service._generate_unsubscribe_header([custom_header])

    # Assert
    assert header == custom_header
