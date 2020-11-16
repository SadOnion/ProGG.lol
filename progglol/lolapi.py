
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
cwd = os.getcwd()

settings = lolapi.get_default_config()
apiMode = os.getenv('API_MODE')

if apiMode == 'kernel':
    settings['pipeline'] = {
        'Cache': {},
        'SimpleKVDiskStore': {
            'package': 'cassiopeia_diskstore',
            'path': cwd + '\\tmp'
        },
        'DDragon': {},
        'Kernel': {
            'server_url': os.getenv('API_KERNEL_URL'),
            'port': os.getenv('API_KERNEL_PORT')
        }
    }
elif apiMode == 'riot':
    settings['pipeline'] = {
        'Cache': {},
        'SimpleKVDiskStore': {
            'package': 'cassiopeia_diskstore',
            'path': cwd + '\\tmp'
        },
        'DDragon': {},
        'RiotAPI': {
            'api_key': os.getenv('API_RIOT_KEY')
        }
    }
else:
    exit(1)

lolapi.apply_settings(settings)

region = os.getenv('DEFAULT_REGION')

if region != '':
    lolapi.set_default_region(region)
else:
    lolapi.set_default_region('EUNE')

# cache champs
champions = lolapi.get_champions()
