
import cassiopeia as lolapi
from dotenv import load_dotenv
import pathlib
import os

TIER_SHORT = {
    lolapi.Tier.iron: 'I',
    lolapi.Tier.bronze: 'B',
    lolapi.Tier.silver: 'S',
    lolapi.Tier.gold: 'G',
    lolapi.Tier.platinum: 'P',
    lolapi.Tier.diamond: 'D',
    lolapi.Tier.master: 'M',
    lolapi.Tier.grandmaster: 'GM',
    lolapi.Tier.challenger: 'CH',
}

DIVISION_SHORT = {
    lolapi.Division.one: '1',
    lolapi.Division.two: '2',
    lolapi.Division.three: '3',
    lolapi.Division.four: '4',
}


load_dotenv(verbose=True)
cwd = pathlib.Path(os.getcwd())

# cache champs
settings = lolapi.get_default_config()
settings['pipeline'] = {
    'Cache': {},
    'SimpleKVDiskStore': {
        'package': 'cassiopeia_diskstore',
        'path': str(cwd / 'cass_tmp')
    },
    'DDragon': {},
    'RiotAPI': {
        'api_key': os.getenv('RIOT_API_KEY')
    }
}

lolapi.apply_settings(settings)
lolapi.set_default_region('EUNE')

# cache champs
champions = lolapi.get_champions()
