# Mending Multiplier

This datapack makes it easier to modify the xp multiplier when using the mending enchantment. The datapack, by default, is vanilla values.

If you used to use Purpur's `gameplay-mechanics.mending-multiplier` option, then

1. [download the datapack](https://download-directory.github.io/?url=https%3A%2F%2Fgithub.com%2FPurpurMC%2FPurpurPacks%2Ftree%2Fmaster%2Fpacks%2Fmending_multiplier)
2. go into `data/minecraft/enchantment/mending.json`. You'll see the following section:

```json
    "minecraft:repair_with_xp": [
      {
        "effect": {
          "type": "minecraft:multiply",
          "factor": 2.0
        }
      },
      {
        "effect": {
          "type": "minecraft:multiply",
          "factor": 1.0
        }
      }
    ]
```

Change the `1.0` value to be the same as what the value of `gameplay-mechanics.mending-multiplier` used to be in your config.
