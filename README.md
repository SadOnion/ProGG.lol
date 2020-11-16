# ProGG.lol

ProGG.lol is an application designed to help you in League of Legends. The main features are:
- champion select analysis - the application looks up your teammates, showing you their rank and their performance on chosen champions.
- in game analysis - ProGG.lol looks up your enemies, showing you their rank and their performance on chosen champions.
- previous champion selects - ProGG.lol saves previous (or dodged) champion selects to help you target ban enemies.

## Installation

Requires Python3.

- clone the repo
- run: `pip install -r requirements.txt`
- set up the `.env` file:
  - `API_MODE=riot`: get a key from https://developer.riotgames.com/ and set `API_RIOT_KEY`
  - `API_MODE=kernel`: set up https://github.com/meraki-analytics/kernel and set `API_KERNEL_URL` and `API_KERNEL_PORT`
  - optional: set `DEFAULT_REGION` to your region (this option preloads static data)

## Running

Currently only supports EUW and EUNE regions.

- inside repo/progglol run `python progglol.py`

The first run is going to take a while (5-10s) because the application downloads static data and then it'll ask for the game directory path.

## Disclaimer

ProGG.lol isn't endorsed by Riot Games and doesn't reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.
