# Infinity works with any arrow

This datapack makes it so infinity works on any arrow that's under the #arrows minecraft tag.

If you'd like to make it work on only specific types of arrows, you can

1. [download the datapack](https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2FPurpurMC%2FPurpurPacks%2Ftree%2Fmaster%2Fpacks%2Finfinity-works-with-any-arrow)
2. go into `data/minecraft/enchantment/infinity.json` and change

```json
            "items": [
              "#minecraft:arrows"
            ]
```

to

```json
            "items": [
              "minecraft:arrow",
              "minecraft:tipped_arrow",
              "minecraft:spectral_arrow"
            ]
```

You can choose to remove any of the values under item depending on what you want.
