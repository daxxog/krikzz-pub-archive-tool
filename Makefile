.PHONY: help
help:
	@echo "available targets -->\n"
	@cat Makefile | grep ".PHONY" | grep -v ".PHONY: _" | sed 's/.PHONY: //g'


.PHONY: build-env
build-env:
	if [ ! -d build-env ]; then \
		pyenv install -s; \
		python3 -m venv build-env; \
		build-env/bin/python3 -m pip install --upgrade pip setuptools wheel; \
		build-env/bin/python3 -m pip install -r requirements.dev.txt; \
	fi


.PHONY: build
build: build-env
	build-env/bin/python3 -m build


.PHONY: release
release: build-env version-bump
	make build
	build-env/bin/python3 -m twine upload --repository krikzz-pub-archive-tool dist/*
	git add VERSION
	git commit -m "built krikzz-pub-archive-tool@$$(cat VERSION)"
	git push
	git tag -a "$$(cat VERSION)" -m "tagging version $$(cat VERSION)"
	git push origin $$(cat VERSION)


.PHONY: version-bump
version-bump:
	scripts/version-bump.sh


.PHONY: freeze
freeze:
	pyenv install -s
	python3 -m venv freeze-env
	freeze-env/bin/python3 -m pip install --upgrade pip setuptools wheel
	freeze-env/bin/python3 -m pip install -r requirements.txt
	freeze-env/bin/python3 -m pip freeze | grep "==" | grep -v '# Editable Git install' | tee requirements.frozen.txt
	rm -rf freeze-env
	git diff requirements.frozen.txt
