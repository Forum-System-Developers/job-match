import logging
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from functools import lru_cache

from app.core.config import get_settings
from app.schemas.common import MessageResponse

logger = logging.getLogger(__name__)


class MailService:
    """
    MailService is a class responsible for sending emails using an SMTP server.

    Attributes:
        smtp_server (str): The SMTP server address.
        smtp_port (int): The SMTP server port.
        username (str): The username for the SMTP server.
        password (str): The password for the SMTP server.
        from_email (str): The sender's email address.

    Methods:
        send_mail(self, to_email: str, subject: str, body: str, list_unsubscribe: list[str] | None = None) -> MessageResponse:
            Sends an email to the specified recipient.
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_email: str,
    ) -> None:
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    def send_mail(
        self,
        to_email: str,
        subject: str,
        body: str,
        list_unsubscribe: list[str] | None = None,
    ) -> MessageResponse:
        """
        Sends an email to the specified recipient.

        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body content of the email.
            list_unsubscribe (list[str] | None, optional): A list of unsubscribe links. Defaults to None.

        Returns:
            MessageResponse: An object containing the response message.

        Raises:
            Exception: If there is an error sending the email.
        """
        message = self._create_message(
            to_email=to_email,
            subject=subject,
            body=body,
            list_unsubscribe=list_unsubscribe,
        )

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(self.from_email, to_email, message.as_string())
                logger.info(f"Message sent to {to_email}")
                return MessageResponse(
                    message=f"Message sent successfully to {to_email}"
                )
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return MessageResponse(message=f"Error sending email to {to_email}")

    def _create_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        list_unsubscribe: list[str] | None = None,
    ) -> MIMEMultipart:
        """
        Create an email message with the specified parameters.

        Args:
            to_email (str): The recipient's email address.
            subject (str): The subject of the email.
            body (str): The body content of the email.
            list_unsubscribe (list[str] | None, optional): A list of unsubscribe URLs or email addresses. Defaults to None.

        Returns:
            MIMEMultipart: The constructed email message.
        """
        unsubscribe_header = self._generate_unsubscribe_header(list_unsubscribe)
        message = MIMEMultipart()
        message["From"] = self.from_email
        message["To"] = to_email
        message["Subject"] = subject
        message["Date"] = formatdate(localtime=True)
        message["Message-ID"] = make_msgid()
        message["List-Unsubscribe"] = Header(unsubscribe_header)
        message.attach(MIMEText(body, "html"))
        logger.info(f"Message created for {to_email}")

        return message

    def _generate_unsubscribe_header(
        self,
        list_unsubscribe: list[str] | None = None,
    ) -> str:
        """
        Generates the List-Unsubscribe header for an email.

        Args:
            list_unsubscribe (list[str] | None): A list of unsubscribe URLs or email addresses.
                                                 If None, a default mailto unsubscribe link is used.

        Returns:
            str: A comma-separated string of unsubscribe URLs or email addresses.
        """
        if list_unsubscribe is None:
            list_unsubscribe = [f"<mailto:{self.from_email}?subject=unsubscribe>"]

        return ", ".join(list_unsubscribe)


@lru_cache
def get_mail_service():
    return MailService(
        smtp_server=get_settings().SMTP_SERVER,
        smtp_port=get_settings().SMTP_PORT,
        username=get_settings().SMTP_USERNAME,
        password=get_settings().SMTP_PASSWORD,
        from_email=get_settings().SMTP_FROM_EMAIL,
    )
