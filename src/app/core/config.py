# # The reason to ignore "assignment" https://github.com/pydantic/pydantic/issues/3143
# # mypy: disable-error-code="assignment"
# import secrets
# from functools import lru_cache
# from typing import List, Optional, Union

# from pydantic import field_validator, AnyHttpUrl
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     API_V1_STR: str = "/api/v1"
#     BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
#     VERSION: Optional[str] = "9.9.9.9"

#     @field_validator("BACKEND_CORS_ORIGINS", check_fields=False)
#     def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
#         if isinstance(v, str) and not v.startswith("["):
#             return [i.strip() for i in v.split(",")]
#         else:
#             return v

#     PROJECT_NAME: str = "qc-web"

#     PYDEVD: bool = False
#     PYDEVD_PORT: Optional[int] = None
#     PYDEVD_HOST: Optional[str] = None

#     class Config:
#         case_sensitive = True
#         env_file = ".env"
#         env_file_encoding = "utf-8"


# @lru_cache()
# def get_settings() -> Settings:
#     return Settings()
