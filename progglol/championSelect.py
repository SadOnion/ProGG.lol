from player import Player


class ChampionSelect:
    def __init__(self, players):
        self.players = players

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
