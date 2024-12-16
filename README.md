<img src="rephera-logo.png" alt= "logo" width="300px"
style = "margin: 20px auto; display: block;"/>

---

# Project Rephera

**WEB application created for Telerik Academy**

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [License](#license)

## Introduction

Visit our <a href='https://www.rephera.com'>website</a> to explore this project!

**Project Rephera** is a backend web application built using the FASTApi framework for creating a job matching platform. It provides a RESTful API for user authentication, job and applications posting, applicant and company user management, and role-based permissions.

The **database** app can be found <a href='https://github.com/Forum-System-Developers/job-match-db'>here</a>.

The **frontend** app can be found <a href='https://github.com/Forum-System-Developers/job-match-frontend'>here</a>.

## Features
- **User Authentication & Authorization**: Supports secure login and role-based access.
- **Job Advertisement Management**: Create, read and update job ads.
- **Job Application Management**: Create, read and update job applications.
- **Company profile Management**: Manage companies and their job advertisements.
- **Professional Profile Management**: Manage applicants and their applications.
- **Role-Based Access Control**: Restrict access based on user roles and permissions.

## Installation

To install and run the project locally, follow these steps:

### Prerequisites
- Python 3.12 or later
- Pyenv

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Forum-System-Developers/job-match.git
   cd job-match
   ```

2. **Install dependencies**:
   - For UNIX based systems run `make init_mac` in the console
   - For Windows users run the `init_win.ps1` file

3. **Set up environment variables**:
   Create a `.env` file with the following content:
   ```bash
   cp src/.env_template .env
   # Open .env and set the required configurations (e.g., database URL, JWT secret key)
   ```

4. **Run the application**:
   ```bash
   python src/run_server.py
   ```

   The API will be available at `http://127.0.0.1:8000`.

## Usage

Once the application is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://127.0.0.1:8000/swagger](http://127.0.0.1:8000/swagger)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

You can also use tools like Postman or `curl` to test the API endpoints.

## Project Structure

```plaintext
src/app/
├── api/
│   └── api_v1/
│       └── endpoints/         # API route definitions
├── core/
│   └──  config.py             # Configuration settings
├── main.py                    # Entry point of the application
├── exceptions/
│   └── customs_exceptions.py  # Custom exceptions
├── schemas/                   # Pydantic models for request/response schemas
├── services/                  # Core application logic and services
│   ├── enums/                 # Enums used across the app
│   └── utils/                 # Utility functions for common tasks in the services
├── utils/                     # Utility functions for common tasks
├── pyproject.toml             # Project configuration and dependencies
├── README.md                  # Project documentation
└── tests/                     # Unit and integration tests
```

## Testing

To run the tests, use the following command:

```bash
pytest tests
```

This will run all tests in the `tests/` directory. Ensure that your `.env` file or test configuration uses a separate test database to avoid modifying production data.

## License

This project is licensed under the [MIT License](LICENSE).

---
