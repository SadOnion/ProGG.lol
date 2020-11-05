
import cassiopeia as cass
from dotenv import load_dotenv
import pathlib
import os


load_dotenv(verbose=True)
cwd = pathlib.Path(os.getcwd())

# cache champs
settings = cass.get_default_config()
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

cass.apply_settings(settings)
cass.set_default_region('EUNE')

champions = cass.get_champions()
