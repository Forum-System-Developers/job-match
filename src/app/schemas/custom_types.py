from pydantic import condecimal, constr

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,30}$"


Salary = condecimal(gt=0, max_digits=10, decimal_places=2)

Username = constr(
    strip_whitespace=True,
    min_length=5,
    max_length=30,
    pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
)

Password = constr(min_length=8, max_length=22)
