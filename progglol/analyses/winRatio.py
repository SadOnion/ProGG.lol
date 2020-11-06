from analysis import Analysis


class WinRatio(Analysis):
    def run(self):
        winCount = 0
        loseCount = 0
        for leagueEntry in self.player.summoner.league_entries:
            winCount += leagueEntry.wins
            loseCount += leagueEntry.losses

        return winCount / (winCount + loseCount)
