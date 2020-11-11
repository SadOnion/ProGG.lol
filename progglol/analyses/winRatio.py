from analysis import Analysis
from lolapi import lolapi, TIER_SHORT, DIVISION_SHORT


class WinRatio(Analysis):

    def soloq(self):
        leagueEntries = self.player.summoner.league_entries

        if lolapi.Queue.ranked_solo_fives in leagueEntries:
            leagueEntry = leagueEntries[lolapi.Queue.ranked_solo_fives]
            wins = leagueEntry.wins
            losses = leagueEntry.losses
            if wins + losses == 0:
                return ''

            return 'SOLOQ: {}% ({}W {}L)'.format(round(100 * wins / (wins + losses)), wins, losses)

        return ''

    def flexq(self):
        leagueEntries = self.player.summoner.league_entries

        if lolapi.Queue.ranked_flex_fives in leagueEntries:
            leagueEntry = leagueEntries[lolapi.Queue.ranked_flex_fives]
            wins = leagueEntry.wins
            losses = leagueEntry.losses
            if wins + losses == 0:
                return ''

            return 'FLEXQ: {}% ({}W {}L)'.format(round(100 * wins / (wins + losses)), wins, losses)

        return ''

    def run(self):
        soloq = self.soloq()
        flexq = self.flexq()

        if soloq and flexq:
            return '{} | {}'.format(soloq, flexq)

        if soloq:
            return soloq

        if flexq:
            return flexq

        return ''
