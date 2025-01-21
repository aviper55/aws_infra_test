PIP ?= pip3

target:
	$(info ${HELP_MESSAGE})
	@exit 0


all: clean install

clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	rm -rf venv
	rm -rf htmlcov
	rm -rf .pytest_cache



runTests:
	. ./venv/bin/activate 
	pytest -v --disable-socket tests


install: 
	${PIP} install virtualenv
	python3 -m venv venv
	. ./venv/bin/activate && ${PIP} install -r requirements.txt
	



shell:
	. ./venv/bin/activate

#############
#  Helpers  #
#############

define HELP_MESSAGE

	Usage: make <command>

	Commands:

	install   Install application and dev dependencies defined in requirements.txt and Run Tests
	shell     Spawn a virtual environment shell
	runTests  Run unit test locally using mocks

endef