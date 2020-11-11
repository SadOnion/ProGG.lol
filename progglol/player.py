from lolapi import lolapi, TIER_SHORT, DIVISION_SHORT
from analyses.summonerStats import SummonerStats
from analyses.championStats import ChampionStats
import asyncio


class Player:
    def __init__(self, summonerName, summonerPuuid, team, assignedRole):
        self.summonerName = summonerName
        self.summonerPuuid = summonerPuuid
        self.team = team
        self.assignedRole = assignedRole

        self.champion = None
        self.bannedChampions = {}
        self.summoner = None
        self.analysis = ''
        self.championAnalysis = ''

        if self.summonerName:
            self.summoner = lolapi.Summoner(name=self.summonerName)

    async def setChampion(self, champId):
        if champId != 0:
            if self.champion and self.champion.id == champId:
                return False

            self.champion = lolapi.Champion(id=champId)
            self.champion.image.image

            await self.runAnalysis()

            return True

        return False

    def setBannedChampion(self, actionId, bannedChampionId):
        if bannedChampionId != 0:
            if actionId in self.bannedChampions:
                return False

            self.bannedChampions[actionId] = lolapi.Champion(
                id=bannedChampionId)
            self.bannedChampions[actionId].image.image
            return True

        return False

    def getRank(self):
        if self.summoner:
            ranks = self.summoner.ranks

            soloqStr = 'UN'
            flexStr = 'UN'

            if lolapi.Queue.ranked_solo_fives in ranks:
                soloq = ranks[lolapi.Queue.ranked_solo_fives]
                soloqStr = '{}{}'.format(
                    TIER_SHORT[soloq.tier], DIVISION_SHORT[soloq.division])

            if lolapi.Queue.ranked_flex_fives in ranks:
                flex = ranks[lolapi.Queue.ranked_flex_fives]
                flexStr = '{}{}'.format(
                    TIER_SHORT[flex.tier], DIVISION_SHORT[flex.division])

            return '{} | {}'.format(soloqStr, flexStr)

        return ''

    async def runAnalysis(self):
        # self.analysis = '{} {}'.format(
        #     WinRatio(self).run(), WinRatioChampion(self).run())
        self.analysis = SummonerStats(self).run()
        self.championAnalysis = ChampionStats(self).run()
