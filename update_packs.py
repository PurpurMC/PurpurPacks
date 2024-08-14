import os
import json


# Function to increment the version number
def increment_version(version, major=False):
    major_version, minor_version = map(int, version.split('.'))
    if major:
        major_version += 1
        minor_version = 0
    else:
        minor_version += 1
    return f"{major_version}.{minor_version}"


# Function to update modrinth.json files
def update_modrinth_files(directory, new_name, changelog, new_versions, major_version=False, update_version=True):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "modrinth.json":
                file_path = os.path.join(root, file)

                with open(file_path, 'r') as f:
                    data = json.load(f)

                # Update version number if required
                if update_version:
                    current_version = data.get("version_number", "1.0")
                    new_version = increment_version(current_version, major=major_version)
                    data["version_number"] = new_version
                else:
                    new_version = data.get("version_number", "1.0")  # Use current version if not updating

                # Update name with the version placeholder
                data["name"] = new_name.replace("{ver}", new_version)

                # Update changelog
                data["changelog"] = changelog

                # Add new game versions
                if "game_versions" not in data:
                    data["game_versions"] = []
                data["game_versions"].extend(new_versions)
                data["game_versions"] = list(set(data["game_versions"]))  # Remove duplicates

                # Write the updated data back to the file
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                    f.write('\n')

                print(f"Updated {file_path}")


# Example usage
directory = "packs"
new_name = "v{ver} Update"
changelog = "Starts preparing support easier updating. Adds a 'version_info.txt' file. Also adds 'support' for 1.21.1, though not particularly necessary"
new_versions = ["1.21.1"]
major_version_increment = False  # Set to True to increment the major version
update_version = False  # Set to False to skip version updates

update_modrinth_files(directory, new_name, changelog, new_versions, major_version_increment, update_version)
