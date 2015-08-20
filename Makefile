# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


PYTHON_VERSION = 3
WHEEL_DIR = /tmp/wheelhouse
USE_WHEEL = --use-wheel --no-index --find-links=$(WHEEL_DIR)
PIP = env/bin/pip
PY = env/bin/python


help:
	@echo "Some usefull development shortcuts."
	@echo "  clean      Remove all generated files."
	@echo "  setup      Setup development environment."
	@echo "  test       Run tests and analysis tools."
	@echo "  wheel      Build package wheel and save in '$(WHEEL_DIR)'."
	@echo "  wheels     Build dependencie wheels and save in '$(WHEEL_DIR)'."
	@echo "  publish    Build and upload package to pypi.python.org"


clean:
	rm -rf env
	rm -rf build
	rm -rf dist
	rm -rf *.egg
	rm -rf *.egg-info
	find | grep -i ".*\.pyc$$" | xargs -r -L1 rm


virtualenv: clean
	virtualenv -p /usr/bin/python$(PYTHON_VERSION) env
	$(PIP) install wheel


wheels: virtualenv
	$(PIP) wheel --wheel-dir=$(WHEEL_DIR) -r requirements.txt
	$(PIP) wheel --wheel-dir=$(WHEEL_DIR) -r test_requirements.txt
	$(PIP) wheel --wheel-dir=$(WHEEL_DIR) -r develop_requirements.txt


wheel: test
	$(PY) setup.py bdist_wheel
	mv dist/*.whl $(WHEEL_DIR)


setup: virtualenv
	$(PIP) install $(USE_WHEEL) -r requirements.txt
	$(PIP) install $(USE_WHEEL) -r test_requirements.txt
	$(PIP) install $(USE_WHEEL) -r develop_requirements.txt


test: setup
	screen -S testserver -d -m $(PY) -m dataserv.app
	$(PY) setup.py test
	screen -S testserver -X kill


publish: test
	$(PY) setup.py register sdist upload


# import pudb; pu.db # set break point
