from player import Player


class ChampionSelect:
    def __init__(self, players, mySummonerName):
        self.players = players

        for player in players.values():
            if player.summonerName == mySummonerName:
                self.me = player
                break

    def setPlayerChampion(self, cellId, champId):
        return self.players[cellId].setChampion(champId)

    def setPlayerBannedChampion(self, cellId, actionId, bannedChampionId):
        return self.players[cellId].setBannedChampion(actionId, bannedChampionId)

    def getTeam(self, teamId):
        ret = []
        for player in self.players.values():
            if player.team == teamId:
                ret.append(player)

        return ret

    def getOurTeam(self):
        return self.getTeam(self.me.team)

    def getTheirTeam(self):
        if self.me.team == 1:
            return self.getTeam(2)
        elif self.me.team == 2:
            return self.getTeam(1)
