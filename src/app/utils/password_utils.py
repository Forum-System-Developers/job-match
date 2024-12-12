import logging
import secrets
import string

from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hashes the given password using bcrypt.
    """
    hash_password = context.hash(password)
    logger.info("Password hashed")

    return hash_password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that the given plain password matches the hashed password.
    """
    password = context.verify(plain_password, hashed_password)
    logger.info("Password verified")

    return password


def generate_patterned_password(length: int = 16) -> str:
    """
    Generate a random password with a specified length that includes at least one uppercase letter,
    one lowercase letter, one digit, and one special character.

    Args:
        length (int): The length of the password to be generated. Default is 16.

    Returns:
        str: A randomly generated password string.
    """
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special_characters = "!@#$%^&*()-_=+\\|;:'\",.<>/?"

    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special_characters),
    ]
    all_characters = uppercase + lowercase + digits + special_characters
    password.extend(secrets.choice(all_characters) for _ in range(length - 4))
    secrets.SystemRandom().shuffle(password)
    return "".join(password)
