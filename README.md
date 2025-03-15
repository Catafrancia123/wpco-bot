![Version](https://img.shields.io/badge/version-0.3.2-blue?style=plastic) [![Discord](https://img.shields.io/discord/990326151987724378?logo=discord&logoColor=white&color=5865F2)](https://discord.gg/fAH8GCTJDA) 
# wpco-bot
This repository is the code to host the **World Peace Control Organization**'s bot. It's meant to be locally hosted, but you can host it on any platform. Currently, its being hosted at [Discloud](https://docs.discloud.com/en).
> [!NOTE]
> The bot isn't fully completed yet. There are many commands to add or even debug (sorry for my bad code - catamapp). And there is a risk to fall victim to a unidentified error, which for a normal person sounds confusing.

# Download
## Prerequesites/Dependencies
What you need to run this is basically just the newest Python version, find [here](https://python.org "Official Python Website"). And some 3rd party packages.

- `discord.py` - This is what discord package the bot runs on.
- `rich` (local) - This adds colors and many other stuff you cant do in basic python.
- `playsound3` (local) - This plays a sound to alert you that the bot is ready.
- `pymongo` (database) - This is the alternative to the basic `json` save files (only use this if you have MongoDB set up).

> [!NOTE]
> The packages with `(local)` tag have to be installed to prevent any errors in the file (i just used them to make your command line look better lol - catamapp)

If you want to install these packages fast, run the `setup.py` file.

## Running
You can run the `main.py` file to run the bot with your own token (i aint sharing tokens to everyone!!!).
