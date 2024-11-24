import uuid

VALID_COMPANY_ID = uuid.uuid4()
VALID_COMPANY_NAME = "Test Company"
VALID_COMPANY_USERNAME = "test_username"
VALID_COMPANY_DESCRIPTION = "Test Description"
VALID_COMPANY_ADDRESS_LINE = "Test Address Line"
VALID_COMPANY_EMAIL = "test_company_email@example.com"
VALID_COMPANY_PHONE_NUMBER = "1234567890"

VALID_COMPANY_NAME_2 = "Test Company 2"
VALID_COMPANY_DESCRIPTION_2 = "Test Description 2"

VALID_PASSWORD = "test_password"
HASHED_PASSWORD = "hashed_password"

VALID_JOB_AD_ID = uuid.uuid4()
VALID_PROFESSIONAL_ID = uuid.uuid4()
VALID_JOB_APPLICATION_ID = uuid.uuid4()
VALID_REQUIREMENT_ID = uuid.uuid4()

VALID_CITY_ID = uuid.uuid4()
VALID_CITY_NAME = "Test City"

VALID_CITY_ID_2 = uuid.uuid4()
VALID_CITY_NAME_2 = "Test City 2"

NON_EXISTENT_ID = uuid.uuid4()
NON_EXISTENT_USERNAME = "non_existent_username"

COMPANY = {
    "id": VALID_COMPANY_ID,
    "name": VALID_COMPANY_NAME,
    "description": VALID_COMPANY_DESCRIPTION,
    "address_line": VALID_COMPANY_ADDRESS_LINE,
    "city": VALID_CITY_NAME,
    "email": VALID_COMPANY_EMAIL,
    "phone_number": VALID_COMPANY_PHONE_NUMBER,
}
