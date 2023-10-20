discord bot that plays ambience. forever.

# usage
fields uses [PDM](https://pdm.fming.dev) as its primary dependency management tool. if you don't want to use PDM, you can instead use the `requirements-windows.txt` and `requirements-linux.txt` files to create a virtual environment and install all necessary packages. fields has been tested on Python >=3.11.

a separate discord bot should be created for each individual sound file you want to play. one bot is not capable of playing multiple files simultaneously, however one bot *is* capable of playing a single sound file to multiple channels simultaneously. fields expects two things: a `config.json` in the root directory and the `BOT_TOKEN` environment variable to be set to the discord bot token. (`.env` files are supported!) to set up the `config.json` file, simply use the `exampleconfig.json` file provided and rename it. see the [config](#config) for details on fields. (most audio files are *really* loud when played via discord! consider adjusting the `volume` parameter in the config)

new audio should be placed in the `audio/` folder, and some audio is already provided. `wind.mp3` is an eerie gale of wind, and `chirp.mp3` is a *very* intermittent smoke alarm beep.

to run the bot, a PDM script is provided: `pdm run start`. if you are not using PDM, running `python src/fields` from the root directory will also start the bot.

# config
* `audioPath` - absolute or relative path to the audio file to play
* `channelIDs` - list of numerical channel IDs to join and play audio
* `volume` - percentage volume to play audio at. see [this](https://discordpy.readthedocs.io/en/stable/api.html?highlight=ffmpegpcmaudio#discord.PCMVolumeTransformer.volume) section in the discord.py docs for how volume works.
