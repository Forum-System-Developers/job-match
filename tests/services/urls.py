API_BASE_URL = "http://localhost:7999/api/v1"

CATEGORIES_URL = f"{API_BASE_URL}/categories"

CITIES_URL = f"{API_BASE_URL}/cities"
CITY_BY_ID_URL = f"{CITIES_URL}/{{city_id}}"
CITY_BY_NAME_URL = f"{CITIES_URL}/by-name/{{city_name}}"

COMPANIES_URL = f"{API_BASE_URL}/companies"
COMPANY_BY_ID_URL = f"{COMPANIES_URL}/{{company_id}}"
COMPANY_BY_USERNAME_URL = f"{COMPANIES_URL}/by-username/{{username}}"
COMPANY_BY_EMAIL_URL = f"{COMPANIES_URL}/by-email/{{email}}"
COMPANY_BY_PHONE_NUMBER_URL = f"{COMPANIES_URL}/by-phone-number/{{phone_number}}"
COMPANY_UPDATE_URL = f"{COMPANIES_URL}/{{company_id}}"
COMPANY_LOGO_URL = f"{COMPANIES_URL}/{{company_id}}/logo"


JOB_ADS_URL = f"{API_BASE_URL}/job-ads"
JOB_AD_BY_ID_URL = f"{JOB_ADS_URL}/{{job_ad_id}}"
JOB_AD_ADD_SKILL_URL = f"{JOB_ADS_URL}/{{job_ad_id}}/skills/{{skill_id}}"


PROFESSIONALS_URL = f"{API_BASE_URL}/professionals"
PROFESSIONAL_BY_USERNAME_URL = f"{PROFESSIONALS_URL}/by-username/{{username}}"
PROFESSIONAL_BY_EMAIL_URL = f"{PROFESSIONALS_URL}/by-email/{{email}}"
