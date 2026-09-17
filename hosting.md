# Build and host the static site

This public site is fully static. Hosting it does not require a Python process,
WebSocket, terminal server, robot connection, or always-on workstation.

## Build locally

With `uv`:

```bash
cd docs/gokuls_droid_posttraining
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
make html \
  SPHINXBUILD=.venv/bin/sphinx-build \
  PYTHON=.venv/bin/python
```

With an activated Python environment:

```bash
python -m pip install -r requirements.txt
make html
```

Open `_build/html/index.html`, or test through a local static server:

```bash
make serve
```

The local server is only for preview and can be stopped after inspection.

## Public-safety check

```bash
make safety
```

The check rejects likely credentials, private-network addresses, absolute user
home paths, and known lab identities from public text sources. It complements
secret scanning; it does not replace repository-level protection.

## Portable release archive

```bash
make package
```

Outputs:

```text
_dist/gokuls-droid-posttraining-site.tar.gz
_dist/gokuls-droid-posttraining-site.tar.gz.sha256
```

Extract the archive and upload its inner directory to any static host.

## Cloudflare Pages

When a repository is available, configure:

```text
Root directory: docs/gokuls_droid_posttraining
Build command: python -m pip install -r requirements.txt && make html
Output directory: _build/html
Python: 3.11 or newer
```

Cloudflare builds and serves the static output. No robot-side service is
deployed. Set `DOCS_BASE_URL` to the final absolute site URL if canonical URLs
are required.

## GitHub Pages

In a dedicated documentation repository, a workflow needs:

1. checkout;
2. Python setup;
3. `pip install -r requirements.txt`;
4. `make html`;
5. upload `_build/html` with `actions/upload-pages-artifact`;
6. deploy with `actions/deploy-pages`.

If deploying under a repository subpath:

```bash
DOCS_BASE_URL="https://<account>.github.io/<repository>/" make html
```

Do not add a second Pages deploy workflow to a repository that already owns a
Pages site. Use a separate repository or merge both static outputs into one
artifact.

## Static hosting limitations

The hosted site cannot:

- open a shell;
- connect to robot hardware;
- embed Franka Desk on a private robot network;
- start policy, trainer, or reward processes;
- access local result files.

Those are intentional security properties. Commands in this guide are copied
into terminals on the appropriate machine.

## Release checklist

- Strict Sphinx build succeeds.
- Public-safety check succeeds.
- Navigation works from the deployment subpath.
- External links pass `make linkcheck` or failures are reviewed.
- Archive checksum is published.
- No generated build or environment directory is committed.
- Maturity labels match the available evidence.
- Newly supported methods satisfy the integration contract.
