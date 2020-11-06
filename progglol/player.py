from lolapi import lolapi, TIER_SHORT, DIVISION_SHORT


class Player:
    def __init__(self, summonerName, summonerPuuid, team, assignedRole):
        self.summonerName = summonerName
        self.summonerPuuid = summonerPuuid
        self.team = team
        self.assignedRole = assignedRole

        self.champion = None
        self.bannedChampions = {}

        if self.summonerName:
            self.summoner = lolapi.Summoner(name=self.summonerName)

    def setChampion(self, champId):
        if champId != 0:
            if self.champion and self.champion.id == champId:
                return False

            self.champion = lolapi.Champion(id=champId)
            return True

        return False

    def setBannedChampion(self, actionId, bannedChampionId):
        if bannedChampionId != 0:
            if actionId in self.bannedChampions:
                return False

            self.bannedChampions[actionId] = lolapi.Champion(
                id=bannedChampionId)
            return True

        return False

    def getRank(self):
        if self.summoner:
            ranks = self.summoner.ranks
            soloq = ranks[lolapi.Queue.ranked_solo_fives]
            flex = ranks[lolapi.Queue.ranked_flex_fives]
            return '{}{} | {}{}'.format(
                TIER_SHORT[soloq.tier], DIVISION_SHORT[soloq.division], TIER_SHORT[flex.tier], DIVISION_SHORT[flex.division])

        return ''
