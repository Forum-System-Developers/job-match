export POETRY_ENABLED := 1

.PHONY: help

SHELL=bash

# Show this help
help:
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][[:alnum:]_-]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t

# Install python dependencies
init_mac:
	./init_mac.sh
	source .venv/bin/activate

init_win:
	./init_win.sh
	.venv/Scripts/Activate.ps1

lint:
	@printf "$(CYAN)Running static code analysis$(COFF)\n"
	@printf " >>> $(YELLOW)outdated packages$(COFF)\n"
	pip list --outdated
	@printf " >>> $(YELLOW)isort$(COFF)\n"
	isort --check --color src tests integration_tests
	@printf " >>> $(YELLOW)flake8$(COFF)\n"
	flake8 --statistic --count --exit-zero src tests integration_tests
	@printf " >>> $(YELLOW)black$(COFF)\n"
	black --check --diff src tests integration_tests
	@printf " >>> $(GREEN)All good :)$(COFF)\n"

## Runs black formatter, and isort
fix:
	@printf "$(YELLOW)flake8$(COFF) will $(RED)not be executed$(COFF) in this task.\n"
	@printf " ----> Run '$(YELLOW)make check$(COFF)' to see flake8 results.\n"
	@printf " >>> $(CYAN)Running isort$(COFF)\n"
	isort src tests
	@printf " >>> $(GREEN)isort done$(COFF)\n"
	@printf "$(CYAN)Auto-formatting with black$(COFF)\n"
	black src tests
	@printf " >>> $(GREEN)black done$(COFF)\n"
	@printf "Generating $(CYAN)licenses.md$(COFF) file\n"
