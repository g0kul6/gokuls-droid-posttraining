# Gokul's DROID Post-Training Setup

Portable public Sphinx documentation for DROID reward models and robot-policy
post-training.

This site is intentionally separate from the lab operator handbook. It contains
no interactive terminals, robot UI, private network configuration, or runtime
backend.

Build:

```bash
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
make package \
  SPHINXBUILD=.venv/bin/sphinx-build \
  PYTHON=.venv/bin/python
```

The static HTML is in `_build/html`; the uploadable archive is in `_dist`.
