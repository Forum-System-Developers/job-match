import uuid

from app.sql_app.job_ad.job_ad_status import JobAdStatus

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

VALID_JOB_AD_ID = uuid.uuid4()
VALID_JOB_AD_DESCRIPTION = "Test Description"
VALID_JOB_AD_TITLE = "Test Job Ad"

VALID_JOB_AD_ID_2 = uuid.uuid4()
VALID_JOB_AD_DESCRIPTION_2 = "Test Description 2"
VALID_JOB_AD_TITLE_2 = "Test Job Ad 2"

HASHED_PASSWORD = "hashed_password"
VALID_PASSWORD = "test_password"

VALID_JOB_APPLICATION_ID = uuid.uuid4()
VALID_PROFESSIONAL_ID = uuid.uuid4()
VALID_CATEGORY_ID = uuid.uuid4()
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


JOB_AD = {
    "id": VALID_JOB_AD_ID,
    "company_id": VALID_COMPANY_ID,
    "category_id": VALID_CATEGORY_ID,
    "location_id": VALID_CITY_ID,
    "title": VALID_JOB_AD_TITLE,
    "description": VALID_JOB_AD_DESCRIPTION,
    "min_salary": 1000.00,
    "max_salary": 2000.00,
}

JOB_AD_CREATE = {
    "category_id": VALID_CATEGORY_ID,
    "location_id": VALID_CITY_ID,
    "title": VALID_JOB_AD_TITLE,
    "description": VALID_JOB_AD_DESCRIPTION,
    "min_salary": 1000.00,
    "max_salary": 2000.00,
}

JOB_AD_UPDATE = {
    "title": VALID_JOB_AD_TITLE,
    "description": VALID_JOB_AD_DESCRIPTION,
    "location": VALID_CITY_NAME,
    "min_salary": 1000.00,
    "max_salary": 2000.00,
    "status": JobAdStatus.ACTIVE,
}

JOB_AD_2 = {
    "id": VALID_JOB_AD_ID_2,
    "company_id": VALID_COMPANY_ID,
    "category_id": VALID_CATEGORY_ID,
    "location_id": VALID_CITY_ID,
    "title": VALID_JOB_AD_TITLE_2,
    "description": VALID_JOB_AD_DESCRIPTION_2,
    "min_salary": 1200.00,
    "max_salary": 2300.00,
}
