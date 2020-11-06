
from messages import Messages
import threading
import asyncio

from cass import *


TIER_SHORT = {
    cass.Tier.iron: 'I',
    cass.Tier.bronze: 'B',
    cass.Tier.silver: 'S',
    cass.Tier.gold: 'G',
    cass.Tier.platinum: 'P',
    cass.Tier.diamond: 'D',
    cass.Tier.master: 'M',
    cass.Tier.grandmaster: 'GM',
    cass.Tier.challenger: 'CH',
}

DIVISION_SHORT = {
    cass.Division.one: '1',
    cass.Division.two: '2',
    cass.Division.three: '3',
    cass.Division.four: '4',
}


class Summoner:
    def __init__(self, lobbyPos, ourTeam, connection, summonerId, resultSignal):
        self.ourTeam = ourTeam
        self.lobbyPos = lobbyPos
        self.id = summonerId
        self.connection = connection
        self.resultSignal = resultSignal

        self.name = ''

        self.champId = 0
        self.champName = 'X'
        self.champImage = None

        self.rank = ''

        if self.id != 0:
            asyncio.create_task(self.fetchSummoner())

    def setChamp(self, champId):
        self.champId = champId
        if champId == 0:
            self.champName = 'X'
        else:
            champ = cass.Champion(id=champId)
            self.champImage = champ.image.image
            self.champName = champ.name

        self.resultSignal.emit((Messages.CHAMPSELECT_UPDATED, self))

    async def fetchSummoner(self):
        summoner = await self.connection.request('get', '/lol-summoner/v1/summoners/{}'.format(self.id))

        if summoner.status == 200:
            json = await summoner.json()
            self.name = json['displayName']
            self.puuid = json['puuid']

            cassSummoner = cass.Summoner(name=self.name)
            ranks = cassSummoner.ranks
            soloq = ranks[cass.Queue.ranked_solo_fives]
            flex = ranks[cass.Queue.ranked_flex_fives]
            self.rank = '{}{}|{}{}'.format(
                TIER_SHORT[soloq.tier], DIVISION_SHORT[soloq.division], TIER_SHORT[flex.tier], DIVISION_SHORT[flex.division])

            self.resultSignal.emit((Messages.CHAMPSELECT_UPDATED, self))
