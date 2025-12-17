# Version Info Setup
In every datapack / mod there is a file called `version_info.txt` - this holds information mostly for automation internally, but it could be used externally as well so I have kept it included in the files.

It looks like this
```yml
{
    "data_schema": 1.0,
    "version_number": "Project's current version",
    "project_id": "ID of the project",
    "project_name": "Human readable and formatted name",
    "project_description": "Description of the pack",
    "project_icon": "Icon path",
    "modrinth": {
        "project_id": "Project ID on Modrinth",
        "project_type": "mod",
        "slug": "Modrinth Slug",
        "url": "https://modrinth.com/mod/{slug}"
    }
}
```


## `data_schema`

Defines the schema version of this metadata file.

This exists so tooling can safely evolve over time.
If the structure of this file changes in the future, the schema version can be used to handle older formats gracefully.

## `version_number`
Example: `"4.6"`

This is the release version of this project, it is used when publishing to Modrinth, and building mod-specific versions like `"4.6-fabric"`

## `project_id`
Example: `"AsDf1234`

This is the ID of this project. Currently, this is the same as the Modrinth ID, but it may eventually be a different ID.

## `project_name`
Example: `"Amethyst Beacons"`

A human-readable name for the project, used for generating descriptions and various other things.

## `project_description`
Example: `"Beacon bases can be made of amethyst blocks and budding amethyst. Amethyst can be used as a beacon payment item."`

A short summary of what the project is and does, typically shown on project pages and generated descriptions

## `project_icon`
Example: `"pack.png"`

Generally expected to be pack.png, might be some other path. Used for pack icons and uploads

## `modrinth` Object

**`project_id`**
- Modrinth ID

**`project_type`**
- Allowed values: `mod`, `datapack`, `resourcepack`

**`slug`**
- The slug of the project on modrinth

**`url`**
- The URL of the project

