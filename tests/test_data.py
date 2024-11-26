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
VALID_CATEGORY_ID = uuid.uuid4()

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

PROFESSIONAL_RESPONSE = {
    "id": VALID_PROFESSIONAL_ID,
    "first_name": VALID_PROFESSIONAL_FIRST_NAME,
    "last_name": VALID_PROFESSIONAL_LAST_NAME,
    "email": VALID_PROFESSIONAL_EMAIL,
    "city": VALID_CITY_NAME,
    "description": VALID_PROFESSIONAL_DESCRIPTION,
    "photo": None,
    "status": ProfessionalStatus.ACTIVE,
    "active_application_count": VALID_PROFESSIONAL_ACTIVE_APPLICATION_COUNT,
    "has_private_matches": False,
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

PROFESSIONAL_MODEL = {
    "id": VALID_PROFESSIONAL_ID,
    "city_id": VALID_CITY_ID,
    "username": VALID_PROFESSIONAL_USERNAME,
    "password": VALID_PROFESSIONAL_PASSWORD,
    "description": VALID_PROFESSIONAL_DESCRIPTION,
    "email": VALID_PROFESSIONAL_EMAIL,
    "photo": None,
    "status": ProfessionalStatus.ACTIVE,
    "active_application_count": VALID_PROFESSIONAL_ACTIVE_APPLICATION_COUNT,
    "first_name": VALID_PROFESSIONAL_FIRST_NAME,
    "last_name": VALID_PROFESSIONAL_LAST_NAME,
}

#     # title: str
#     # description: str
#     # location_id: UUID
#     # category_id: UUID
#     # min_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore
#     # max_salary: condecimal(gt=0, max_digits=10, decimal_places=2)  # type: ignore

VALID_JOB_AD_ID_2 = uuid.uuid4()

VALID_JOB_AD_TITLE = "TestJobAd"
VALID_JOB_AD_DESCRIPTION = "Test Description"
VALID_JOB_AD_MIN_SALARY = 1000.00
VALID_JOB_AD_MAX_SALARY = 2000.00

VALID_JOB_AD_TITLE_2 = "TestJobAd2"
VALID_JOB_AD_DESCRIPTION_2 = "Test Description 2"
VALID_JOB_AD_MIN_SALARY_2 = 2000.00
VALID_JOB_AD_MAX_SALARY_2 = 3000.00


JOB_AD_1 = {
    "id": VALID_JOB_AD_ID,
    "title": VALID_JOB_AD_TITLE,
    "description": VALID_JOB_AD_DESCRIPTION,
    "location_id": VALID_CITY_ID,
    "category_id": VALID_CATEGORY_ID,
    "min_salary": VALID_JOB_AD_MIN_SALARY,
    "max_salary": VALID_JOB_AD_MAX_SALARY,
}

JOB_AD_2 = {
    "id": VALID_JOB_AD_ID_2,
    "title": VALID_JOB_AD_TITLE_2,
    "description": VALID_JOB_AD_DESCRIPTION_2,
    "location_id": VALID_CITY_ID,
    "category_id": VALID_CATEGORY_ID,
    "min_salary": VALID_JOB_AD_MIN_SALARY_2,
    "max_salary": VALID_JOB_AD_MAX_SALARY_2,
}

JOB_AD_RESPONSE_1 = {
    "title": VALID_JOB_AD_TITLE,
    "description": VALID_JOB_AD_DESCRIPTION,
    "location_id": VALID_CITY_ID,
    "category_id": VALID_CATEGORY_ID,
    "min_salary": VALID_JOB_AD_MIN_SALARY,
    "max_salary": VALID_JOB_AD_MAX_SALARY,
}

JOB_AD_RESPONSE_2 = {
    "title": VALID_JOB_AD_TITLE_2,
    "description": VALID_JOB_AD_DESCRIPTION_2,
    "location_id": VALID_CITY_ID,
    "category_id": VALID_CATEGORY_ID,
    "min_salary": VALID_JOB_AD_MIN_SALARY_2,
    "max_salary": VALID_JOB_AD_MAX_SALARY_2,
}
