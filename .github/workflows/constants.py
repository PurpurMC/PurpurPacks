AUTHORS = ["granny", "Rhythmic", "PurpurMC"]
AUTHORS_MAP = {"granny": "Owner", "Rhythmic": "Developer", "PurpurMC": "Organization"}
CREDITS = "By PurpurMC"
GITHUB_LINK = "https://github.com/PurpurMC/PurpurPacks"
ISSUES_LINK = "https://github.com/PurpurMC/PurpurPacks/issues"

ALWAYS_EXCLUDED = {"pack-meta.json"}
FABRIC_METADATA_FILES = {"fabric.mod.json"}
QUILT_METADATA_FILES = {"quilt.mod.json"}
FORGE_METADATA_FILES = {"mods.toml"}
NEOFORGE_METADATA_FILES = {"neoforge.mods.toml"}
ALL_LOADER_METADATA = FABRIC_METADATA_FILES | QUILT_METADATA_FILES | FORGE_METADATA_FILES | NEOFORGE_METADATA_FILES