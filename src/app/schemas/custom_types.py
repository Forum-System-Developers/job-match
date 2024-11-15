from pydantic import condecimal

Salary = condecimal(gt=0, max_digits=10, decimal_places=2)
