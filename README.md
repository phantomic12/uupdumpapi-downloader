uupdumpcli

Command-line utility to browse and download UUP files using the UUP dump JSON API.

Install (editable)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Usage

- List builds:

```bash
uupdump list --search "Windows 11" --sort-by-date
```

- Show languages/editions for an update ID:

```bash
uupdump show 123e4567-e89b-12d3-a456-426614174000 --langs --editions --lang en-us
```

- Download files for an update ID:

```bash
uupdump download 123e4567-e89b-12d3-a456-426614174000 \
  --lang en-us --edition professional \
  --out ./downloads --concurrency 4 --no-resume
```

- Verify checksums only:

```bash
uupdump verify 123e4567-e89b-12d3-a456-426614174000 --lang en-us --edition professional --path ./downloads
```

### Work alongside the UUP converter

This project can hand off the downloaded UUP files to the official converter script to build ISOs. The converter project is documented here: [uup-dump/converter](https://git.uupdump.net/uup-dump/converter).

Requirements on Linux/macOS (see converter README for details): `aria2c`, `cabextract`, `wimlib-imagex`, `chntpw`, and `genisoimage`/`mkisofs`.

Example: download a set and convert to ISO with standard WIM compression:

```bash
# Clone the converter (once)
git clone https://git.uupdump.net/uup-dump/converter ./converter

# Download and convert
uupdump download <UPDATE_ID> --lang en-us --edition professional \
  --out ./UUPs --convert --convert-dir ./converter --compress wim
```

Enable virtual editions:

```bash
uupdump download <UPDATE_ID> --lang en-us --edition professional \
  --out ./UUPs --convert --convert-dir ./converter --virtual-editions
```

Notes

- API docs: `https://git.uupdump.net/uup-dump/json-api`
- Respects `HTTP_PROXY`/`HTTPS_PROXY` env vars.

## Build a universal Linux executable

Locally (host toolchain):

```bash
./build.sh
ls -lh dist/uupdump
```

Reproducible (manylinux2014 container):

```bash
./build.sh --manylinux
```

GitHub Releases: push a tag like `v0.1.0` and CI will build and attach `uupdump-linux-x86_64.tar.gz` to the release.


