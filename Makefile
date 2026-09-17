SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?= -W --keep-going
PYTHON ?= python3
SOURCEDIR = .
BUILDDIR = _build

.PHONY: help safety html clean linkcheck serve package

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

safety:
	@$(PYTHON) scripts/public_safety_check.py .

html: safety
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS)

clean:
	@rm -rf "$(BUILDDIR)" "_dist"

linkcheck: safety
	@$(SPHINXBUILD) -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck" \
		--keep-going

serve: html
	@$(PYTHON) -m http.server 8080 --directory "$(BUILDDIR)/html" \
		--bind 127.0.0.1

package: html
	@$(PYTHON) scripts/package_site.py
