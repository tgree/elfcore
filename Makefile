PACKAGE := elfcore
VERSION := 0.1.0

DEPS := LICENSE README.txt setup.cfg setup.py
DEPS += $(shell find . -name '*.py')

.PHONY: $(PACKAGE)
$(PACKAGE): dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl

dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl: $(DEPS) Makefile
	python3 setup.py --quiet sdist bdist_wheel
	python3 -m twine check $@

.PHONY: install
install: $(PACKAGE) uninstall
	sudo pip3 install dist/$(PACKAGE)-$(VERSION)-py3-none-any.whl

.PHONY: uninstall
uninstall:
	sudo pip3 uninstall -y $(PACKAGE)

.PHONY: clean
clean:
	rm -rf build dist *.egg-info
	find . -name "*.pyc" | xargs rm
	find . -name __pycache__ | xargs rm -r

.PHONY: test
test:
	python3 -m flake8 elfcore
