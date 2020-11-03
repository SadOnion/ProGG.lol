from PyQt5 import QtWidgets, uic
import sys
from lcu_driver import Connector
import os

import cassiopeia as cass

from dotenv import load_dotenv
load_dotenv(verbose=True)

cass.set_riot_api_key(os.getenv('RIOT_API_KEY'))
cass.set_default_region('EUNE')

connector = Connector()

champions = cass.get_champions()


summoner = cass.Summoner(name="rdκ")
print(summoner)


def getChampionName(id):
    c = cass.Champion(id=id)
    return c.name


async def getSummonerName(connection, id):
    summoner = await connection.request('get', '/lol-summoner/v1/summoners/{}'.format(id))

    if summoner.status != 200:
        print('couldnt find')
        return 'NOT FOUND'
    else:
        json = await summoner.json()
        return json['displayName']


@connector.ws.register('/lol-champ-select/v1/session', event_types=('UPDATE',))
async def displayLobby(connection, event):
    myTeam = event.data['myTeam']
    theirTeam = event.data['theirTeam']

    os.system('cls')

    print('my team')
    for c in myTeam:
        champName = 'not found'

        if c['championPickIntent'] == 0:
            champName = getChampionName(c['championId'])
        else:
            champName = getChampionName(c['championPickIntent'])

        print('summ name: {} champ name: {}'.format(
            await getSummonerName(connection, c['summonerId']), champName))

    print('their team')
    for c in theirTeam:
        champName = 'not found'

        if c['championPickIntent'] == 0:
            champName = getChampionName(c['championId'])
        else:
            champName = getChampionName(c['championPickIntent'])

        print('summ name: {} champ name: {}'.format(
            await getSummonerName(connection, c['summonerId']), champName))


@connector.ready
async def connect(connection):
    print('LCU API is ready to be used.')


@connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
async def gameflow(connection, event):
    print(str(event.data))


@connector.close
async def disconnect(_):
    print('The client have been closed!')

# starts the connector
# connector.start()
