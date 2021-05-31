.PHONY: help
help:
	@echo "available targets -->\n"
	@cat Makefile | grep ".PHONY" | grep -v ".PHONY: _" | sed 's/.PHONY: //g'


.PHONY: release
release: version-bump
	make tag
	docker push daxxog/fastapi-simple-mutex-server:latest 
	docker push daxxog/fastapi-simple-mutex-server:$$(cat VERSION)
	git add VERSION
	git commit -m "built fastapi-simple-mutex-server@$$(cat VERSION)"
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
