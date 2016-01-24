import re
import pickle
from bs4 import BeautifulSoup
from urllib2 import urlopen

schedule_url = 'http://espn.go.com/mens-college-basketball/team/schedule/_'
score_fmt    = re.compile('(\d{1,3})-(\d{1,3})')
gameid_fmt   = re.compile('gameId=(\d+)')

class Team:
    def __init__(self, name, espn_suffix):
        self.name = name
        self.espn_suffix = espn_suffix
        self.games = []
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return self.__dict__ != other.__dict__

class Game:
    def __init__(self, espn_id, high_score, low_score, winner, loser):
        self.espn_id = espn_id
        self.high_score = high_score
        self.low_score = low_score
        self.winner = winner
        self.loser = loser
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return self.__dict__ != other.__dict__
    def __str__(self):
        return '[%s] %s beats %s %s-%s' % (self.espn_id, self.winner, self.loser, self.high_score, self.low_score)

def get_suffix(espn_url):
    return espn_url.partition('_')[2]

teams_data = urlopen('http://espn.go.com/mens-college-basketball/teams').read()
teams_soup = BeautifulSoup(teams_data)
team_links = teams_soup.select('ul.medium-logos > li a.bi')
teams = [Team(team.text, get_suffix(team['href'])) for team in team_links]

teams = {team.espn_suffix : team for team in teams}
games = {}
for team_num, team in enumerate(teams.values()):
    print 'Fetching team %s/%s...' % (team_num, len(teams))
    schedule_data = urlopen(schedule_url + team.espn_suffix).read()
    schedule_soup = BeautifulSoup(schedule_data)
    game_list = schedule_soup.select('div#showschedule table tr')[2:]
    for game_num, game in enumerate(game_list):
        print '\tGame %s/%s...' % (game_num, len(game_list))
        try:
            score = game.select('li.score')[0].text
            score = score_fmt.match(score)
            high_score = score.group(1)
            low_score = score.group(2)
            if low_score > high_score:
                high_score, low_score = low_score, high_score
        except:
            print ' *** Bad score for %s game %s' % (team.name, game_num)
            continue

        try:
            opponent = get_suffix(game.select('li.team-name a')[0]['href'])
            opponent = teams[opponent]
        except:
            print ' *** Bad opponent for %s game %s' % (team.name, game_num)
            continue

        if game.select('li.game-status.win'):
            winner, loser = team, opponent
        elif game.select('li.game-status.loss'):
            winner, loser = opponent, team
        else:
            print ' *** Game in progress for %s game %s' % (team.name, game_num)
            continue

        try:
            espn_id = gameid_fmt.search(game.select('li.score a')[0]['href']).group(1)
        except:
            print ' *** Bad ESPN game ID for %s game %s' % (team.name, game_num)
            continue

        game_data = Game(espn_id, high_score, low_score, winner, loser)
        if espn_id in games:
            if games[espn_id] != game_data:
                print ' *** Mismatched game information! game_id = %s' % (espn_id)
                print ' *** db has %s' % games[espn_id]
                print ' *** just found %s' % game_data
        else:
            games[espn_id] = game_data

print 'Saving to file...'
db = file('db.pkl', 'w')
pickle.dump(teams, db, pickle.HIGHEST_PROTOCOL)
pickle.dump(games, db, pickle.HIGHEST_PROTOCOL)
db.close()
print 'Complete!'

