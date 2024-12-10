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


JOB_APPLICATIONS_URL = f"{API_BASE_URL}/job-applications"
JOB_APPLICATIONS_ALL_URL = f"{JOB_APPLICATIONS_URL}/all"
JOB_APPLICATIONS_BY_ID_URL = f"{JOB_APPLICATIONS_URL}/{{job_application_id}}"


PROFESSIONALS_URL = f"{API_BASE_URL}/professionals"
PROFESSIONALS_BY_ID_URL = f"{PROFESSIONALS_URL}/{{professional_id}}"
PROFESSIONALS_PHOTO_URL = f"{PROFESSIONALS_URL}/{{professional_id}}/photo"
PROFESSIONALS_CV_URL = f"{PROFESSIONALS_URL}/{{professional_id}}/cv"
PROFESSIONALS_JOB_APPLICATIONS_URL = (
    f"{PROFESSIONALS_URL}/{{professional_id}}/job-applications"
)
PROFESSIONAL_BY_USERNAME_URL = f"{PROFESSIONALS_URL}/by-username/{{username}}"
PROFESSIONAL_BY_EMAIL_URL = f"{PROFESSIONALS_URL}/by-email/{{email}}"
PROFESSIONALS_TOGGLE_STATUS_URL = (
    f"{PROFESSIONALS_URL}/{{professional_id}}/private-matches"
)
PROFESSIONALS_SKILLS_URL = f"{PROFESSIONALS_URL}/{{professional_id}}/skills"


MATCH_REQUESTS_URL = f"{API_BASE_URL}/match-requests"
MATCH_REQUESTS_BY_ID_URL = f"{MATCH_REQUESTS_URL}/job-ads/{{job_ad_id}}/job-applications/{{job_application_id}}"
MATCH_REQUESTS_JOB_ADS_RECEIVED_URL = (
    f"{MATCH_REQUESTS_URL}/job-ads/{{job_ad_id}}/received-matches"
)
MATCH_REQUESTS_JOB_ADS_SENT_URL = (
    f"{MATCH_REQUESTS_URL}/job-ads/{{job_ad_id}}/sent-matches"
)
MATCH_REQUESTS_JOB_APPLICATIONS_URL = (
    f"{MATCH_REQUESTS_URL}/job-applications/{{job_application_id}}"
)
MATCH_REQUESTS_PROFESSIONALS_URL = (
    f"{MATCH_REQUESTS_URL}/professionals/{{professional_id}}"
)
MATCH_REQUESTS_COMPANIES_URL = f"{MATCH_REQUESTS_URL}/companies/{{company_id}}"


SKILLS_URL = f"{API_BASE_URL}/skills"
