from analysis import Analysis
from lolapi import lolapi, TIER_SHORT, DIVISION_SHORT


class ChampionStats(Analysis):

    def run(self):
        if self.player.champion:
            wins = 0
            losses = 0
            kdaSum = 0
            games = 0
            killsSum = 0
            assistsSum = 0
            deathsSum = 0

            for match in self.player.summoner.match_history(queues={lolapi.Queue.ranked_solo_fives, lolapi.Queue.ranked_flex_fives}, seasons={lolapi.Season.season_9}, champions={self.player.champion.id}):
                participant = match.participants[self.player.summoner]
                stats = participant.stats
                if stats.win:
                    wins += 1
                else:
                    losses += 1

                kdaSum += stats.kda
                killsSum += stats.kills
                assistsSum += stats.assists
                deathsSum += stats.deaths
                games += 1

            if games == 0:
                return 'NO GAMES'

            return '{}: {}% ({}W {}L) KDA: {} ({}/{}/{})'.format(self.player.champion.name, round(100 * wins / (wins + losses)), wins, losses, round(kdaSum / games, 2), round(killsSum / games, 2), round(assistsSum / games, 2), round(deathsSum / games, 2))

        return ''
