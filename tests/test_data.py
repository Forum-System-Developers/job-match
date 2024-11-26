import uuid

from app.schemas.professional import ProfessionalCreate, ProfessionalRequestBody
from app.sql_app.professional.professional_status import ProfessionalStatus

VALID_COMPANY_ID = uuid.uuid4()
VALID_COMPANY_NAME = "Test Company"
VALID_COMPANY_USERNAME = "test_username"
VALID_COMPANY_DESCRIPTION = "Test Description"
VALID_COMPANY_ADDRESS_LINE = "Test Address Line"
VALID_COMPANY_EMAIL = "test_company_email@example.com"
VALID_COMPANY_PHONE_NUMBER = "1234567890"

VALID_COMPANY_ID_2 = uuid.uuid4()
VALID_COMPANY_NAME_2 = "Test Company 2"
VALID_COMPANY_DESCRIPTION_2 = "Test Description 2"
VALID_COMPANY_ADDRESS_LINE_2 = "Test Address Line 2"
VALID_COMPANY_EMAIL_2 = "test_company_email2@example.com"
VALID_COMPANY_PHONE_NUMBER_2 = "0987654321"

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

MATCHED_ADS = [
    {"id": uuid.uuid4(), "title": "Backend Developer", "description": "FastAPI project"},
    {"id": uuid.uuid4(), "title": "Frontend Developer", "description": "React project"},
]

COMPANY = {
    "id": VALID_COMPANY_ID,
    "name": VALID_COMPANY_NAME,
    "description": VALID_COMPANY_DESCRIPTION,
    "address_line": VALID_COMPANY_ADDRESS_LINE,
    "city": VALID_CITY_NAME,
    "email": VALID_COMPANY_EMAIL,
    "phone_number": VALID_COMPANY_PHONE_NUMBER,
}

CITY = {
    "id": VALID_CITY_ID,
    "name": VALID_CITY_NAME,
}

VALID_PROFESSIONAL_EMAIL = "test_professional@email.com"
VALID_PROFESSIONAL_USERNAME = "TestP"
VALID_PROFESSIONAL_PASSWORD = "TestPassword@123"
VALID_PROFESSIONAL_FIRST_NAME = "Test"
VALID_PROFESSIONAL_LAST_NAME = "Professional"
VALID_PROFESSIONAL_DESCRIPTION = "Test Description"
VALID_PROFESSIONAL_ACTIVE_APPLICATION_COUNT = 0

PROFESSIONAL = {
    "id": VALID_PROFESSIONAL_ID,
    "first_name": VALID_PROFESSIONAL_FIRST_NAME,
    "last_name": VALID_PROFESSIONAL_LAST_NAME,
    "email": VALID_PROFESSIONAL_EMAIL,
    "city": VALID_CITY_NAME,
    "description": VALID_PROFESSIONAL_DESCRIPTION,
    "photo": None,
    "status": ProfessionalStatus.ACTIVE,
    "active_application_count": VALID_PROFESSIONAL_ACTIVE_APPLICATION_COUNT,
    "matched_ads": None,
}

PROFESSIONAL_REQUEST = ProfessionalRequestBody(
    professional=ProfessionalCreate(
        username=VALID_PROFESSIONAL_USERNAME,
        password=VALID_PROFESSIONAL_PASSWORD,
        email=VALID_PROFESSIONAL_EMAIL,
        first_name=VALID_PROFESSIONAL_FIRST_NAME,
        last_name=VALID_PROFESSIONAL_LAST_NAME,
        description=VALID_PROFESSIONAL_DESCRIPTION,
        city=VALID_CITY_NAME,
    ),
    status=ProfessionalStatus.ACTIVE,
)

UPDATED_PROFESSIONAL = {
    **PROFESSIONAL,
    "description": "Updated description",
}

UPDATED_PROFESSIONAL_RESPONSE = {
    "id": PROFESSIONAL["id"],
    "first_name": PROFESSIONAL["first_name"],
    "last_name": PROFESSIONAL["last_name"],
    "email": PROFESSIONAL["email"],
    "city": PROFESSIONAL["city"],
    "description": UPDATED_PROFESSIONAL["description"],
    "photo": None,
    "status": ProfessionalStatus.ACTIVE,
    "active_application_count": 2,
    "matched_ads": MATCHED_ADS,
}
