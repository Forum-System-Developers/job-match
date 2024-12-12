import string

import pytest

from app.utils.password_utils import generate_patterned_password


def test_generatePatternedPassword_generatesPasswordWithCorrectLength():
    password = generate_patterned_password(16)
    assert len(password) == 16


def test_generatePatternedPassword_containsUppercase():
    password = generate_patterned_password(16)
    assert any(char in string.ascii_uppercase for char in password)


def test_generatePatternedPassword_containsLowercase():
    password = generate_patterned_password(16)
    assert any(char in string.ascii_lowercase for char in password)


def test_generatePatternedPassword_containsDigit():
    password = generate_patterned_password(16)
    assert any(char in string.digits for char in password)


def test_generatePatternedPassword_containsSpecialCharacter():
    special_characters = "!@#$%^&*()-_=+\\|;:'\",.<>/?"
    password = generate_patterned_password(16)
    assert any(char in special_characters for char in password)


def test_generatePatternedPassword_defaultLength():
    password = generate_patterned_password()
    assert len(password) == 16


def test_generatePatternedPassword_customLength():
    custom_length = 20
    password = generate_patterned_password(custom_length)
    assert len(password) == custom_length
