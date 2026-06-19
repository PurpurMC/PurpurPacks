import json
import os

from constants import AUTHORS, AUTHORS_MAP, CREDITS, GITHUB_LINK, ISSUES_LINK
from loader_classes import ALL_LOADER_TEMPLATES, LoaderTemplates


def _build_substitutions(pack_meta: dict, version_suffix: str) -> dict:
    version = pack_meta.get("version_number", "")
    return {
        "{mod-id}": pack_meta.get("id", ""),
        "{version-number}": f"{version}{version_suffix}",
        "{project-name}": pack_meta.get("display_name", ""),
        "{project-description}": pack_meta.get("description", ""),
        "{modrinth-id}": pack_meta.get("modrinth_slug", ""),
        "{github-link}": GITHUB_LINK,
        "{issues-link}": ISSUES_LINK,
        "{icon-path}": "pack.png",
        "{credits}": CREDITS,
        # The three variants cover different quoting styles in the template files.
        '"{authors-list}"': json.dumps(AUTHORS),
        "'{authors-list}'": json.dumps(AUTHORS),
        "{authors-list}": json.dumps(AUTHORS),
        "{authors-map}": json.dumps(AUTHORS_MAP, indent=6),
    }


def _fill_template(text: str, substitutions: dict) -> str:
    for placeholder, value in substitutions.items():
        text = text.replace(placeholder, value)
    return text


def _write_file(pack_dir: str, rel_path: str, content: str) -> None:
    dest = os.path.join(pack_dir, rel_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(content)


def generate_loader_files(pack_dir: str, pack_meta: dict) -> None:
    for template in ALL_LOADER_TEMPLATES:
        subs = _build_substitutions(pack_meta, template.version_suffix)
        raw = template.manifest_path.read_text(encoding="utf-8")
        _write_file(pack_dir, template.output_path, _fill_template(raw, subs))
