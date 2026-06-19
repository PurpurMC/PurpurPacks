# PurpurScripts

Scripts for updating and publishing PurpurPacks datapacks to Modrinth.

## Scripts

| Script | Purpose |
|---|---|
| `update_packs.py` | Updates `pack.mcmeta` and `pack-meta.json` across all packs |
| `main.py` | Builds artifacts and publishes packs to Modrinth |

Both scripts walk the packs directory and operate on every folder that contains a `pack.mcmeta` file.

---

## Environment Variables

### Shared

| Variable | Default | Description |
|---|---|---|
| `PACKS_DIR` | `../../packs` (relative to script) | Path to the root packs directory |
| `DISTRO_DIR` | `../../distribute` (relative to script) | Output directory for built artifacts |
| `DRY_RUN` | `false` | Set to `true` to log what would happen without writing or uploading anything. For `update_packs.py`, the would-be file contents are printed to stdout |
| `SKIP_CI` | `false` | Set to `true` to exit immediately; useful for skipping in CI when no publish is needed (`main.py` only) |

### `update_packs.py`

#### `pack.mcmeta`

| Variable | Default | Description |
|---|---|---|
| `PACK_FORMAT` | *(none)* | New max pack format number (float, e.g. `101.1`). Required to update `pack.mcmeta`; packs are skipped if unset. For format 82+, `supported_formats` is removed from the file (deprecated by Minecraft) |
| `MIN_FORMAT` | *(preserved)* | Override the minimum supported pack format. If unset, the existing `min_inclusive` / `min_format` value is kept |

#### `pack-meta.json`

| Variable | Default | Description |
|---|---|---|
| `VERSION_NUMBER` | *(auto-incremented)* | Explicit version to set (e.g. `3.10`). If unset, the minor version is bumped automatically |
| `INCREMENT_MAJOR` | `false` | Set to `true` to bump the major version instead of minor (`3.9` → `4.0` instead of `3.10`) |
| `VERSION_NAME_TEMPLATE` | `v{version} Update` | Template for the `name` field. `{version}` is replaced with the new version number |
| `CHANGELOG` | *(unchanged)* | Release changelog text. If unset, the existing value is kept |
| `GAME_VERSIONS` | *(unchanged)* | Comma-separated list of game versions to **add** to each pack (e.g. `1.21.9,1.21.10`). Merged with existing versions; any version older than `1.21.9` is automatically removed |

### `main.py`

| Variable | Required | Description |
|---|---|---|
| `MODRINTH_TOKEN` | Yes | Modrinth personal access token for uploading versions |

---

## Usage

### Updating packs

Run `update_packs.py` before a release to bump versions and update format numbers across all packs.

```bash
# Dry run first to preview changes
PACKS_DIR=/path/to/PurpurPacks/packs \
PACK_FORMAT=101.1 \
GAME_VERSIONS=1.21.9,1.21.10 \
CHANGELOG="Update to 1.21.10" \
DRY_RUN=true \
python update_packs.py

# Apply changes
PACKS_DIR=/path/to/PurpurPacks/packs \
PACK_FORMAT=101.1 \
GAME_VERSIONS=1.21.9,1.21.10 \
CHANGELOG="Update to 1.21.10" \
python update_packs.py
```

To set an explicit version instead of auto-incrementing:

```bash
VERSION_NUMBER=4.0 python update_packs.py
```

To bump the major version:

```bash
INCREMENT_MAJOR=true python update_packs.py
```

### Publishing to Modrinth

Run `main.py` after updating packs. It checks each pack's `project_id` against Modrinth and skips any version that already exists.

```bash
# Dry run
PACKS_DIR=/path/to/PurpurPacks/packs \
MODRINTH_TOKEN=your_token_here \
DRY_RUN=true \
python main.py

# Publish
PACKS_DIR=/path/to/PurpurPacks/packs \
MODRINTH_TOKEN=your_token_here \
python main.py
```

---

## `pack-meta.json` Reference

Each pack directory that has a `pack.mcmeta` may also contain a `pack-meta.json` to configure publishing. Packs without a `project_id` are skipped by `main.py`.

```json
{
    "id": "beacon_base_amethyst",
    "display_name": "Amethyst Beacons",
    "description": "Pack description here.",
    "name": "v3.10 Update",
    "version_number": "3.10",
    "project_id": "EP4tesbZ",
    "modrinth_slug": "purpurpacks-amethyst-beacon-base",
    "has_loader_distribution": true,
    "changelog": "Update to 1.21.10",
    "game_versions": ["1.21.9", "1.21.10"],
    "version_type": "release",
    "categories": ["beacon_base"],
    "dependencies": []
}
```

| Field | Description |
|---|---|
| `id` | Internal mod ID used in loader manifests |
| `display_name` | Human-readable name used in loader manifests |
| `description` | Pack description used in loader manifests |
| `name` | Release name shown on Modrinth (updated by `update_packs.py`) |
| `version_number` | Release version (updated by `update_packs.py`) |
| `project_id` | Modrinth project ID. Packs without this are skipped during publishing |
| `modrinth_slug` | Modrinth project slug used in loader manifests |
| `has_loader_distribution` | If `true`, fabric/quilt/forge/neoforge mod jars are also built and published |
| `changelog` | Release changelog shown on Modrinth |
| `game_versions` | List of supported Minecraft versions |
| `version_type` | Modrinth release type: `release`, `beta`, or `alpha` |
| `categories` | Internal category tags (not sent to Modrinth directly) |
| `dependencies` | Modrinth dependency objects appended to loader defaults |
