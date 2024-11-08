import json
import os

# Define the main directory where you want to start searching
main_directory = r"D:\Documents\IdeaProjects\PurpurPacks\packs"


# Function to extract version_number and project_id from modrinth.json
def extract_modrinth_file_info():
    if 'modrinth.json' in files:
        modrinth_file_path = os.path.join(root, 'modrinth.json')
    else: return None

    with open(modrinth_file_path, 'r') as file:
        data = json.load(file)
        project_id = data.get("project_id")
        print(project_id)
        return project_id


def extract_description_from_text():
    if 'pack.mcmeta' in files:
        pack_mcmeta_file_path = os.path.join(root, 'pack.mcmeta')
        print(pack_mcmeta_file_path)
    else: return None

    with open(pack_mcmeta_file_path, 'r') as file:
        content = file.read()
    try:
        data = json.loads(content)
        description = data.get("pack").get("description")
        print(description)
        return description
    except json.JSONDecodeError:
        print(f"Warning: {pack_mcmeta_file_path} not valid JSON")


# Function to write the extracted info into a new file
def write_version_info(project_id, alt_text):
    output_path = os.path.join(main_directory, "CREATED_README.md")
    image_link = os.path.join(root, "pack.png")
    project_link = f"https://modrinth.com/project/{project_id}/versions"
    end_text = f"[![]({image_link} \"{alt_text}\")]({project_link})"
    with open(output_path, 'a') as file:
        file.write(end_text + "\n")


# Walk through the main directory
for root, dirs, files in os.walk(main_directory):
    project_id = extract_modrinth_file_info()
    alt_text = extract_description_from_text()
    current_pack = root
    if project_id is None: continue
    write_version_info(project_id, alt_text)

print("Finished processing all directories.")
