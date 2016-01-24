import pickle
import gaussian
from math import sqrt

INITIAL_MEAN     = 25.0
INTIIAL_STDDEV   = INITIAL_MEAN/3.0
BETA             = INITIAL_MEAN/6.0
DYNAMICS_FACTOR  = INITIAL_MEAN/300.0
DRAW_PROBABILITY = 0.0

class Team:
    def __init__(self, name, espn_suffix):
        self.name = name
        self.espn_suffix = espn_suffix
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    def __ne__(self, other):
        return self.__dict__ != other.__dict__
    def __str__(self):
        return self.name

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

class Rating:
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def conservative_rating(self):
        return self.mean - 3 * self.stddev

    def __repr__(self):
        return 'Rating(mean=%s, stddev=%s)' % (self.mean, self.stddev)


def get_draw_margin_from_draw_prob(draw_prob, beta):
    margin = gaussian.inverse_cdf(0.5*(draw_prob + 1), 0, 1) * sqrt(1 + 1) * beta
    return margin

def true_skill_v(mean_delta, draw_margin, c):
    team_performance_difference = mean_delta / c
    draw_margin = draw_margin / c
    denominator = gaussian.cdf(team_performance_difference - draw_margin)
    if denominator < 1e-161:
        return -team_performance_difference + draw_margin
    return gaussian.at(team_performance_difference - draw_margin) / denominator

def true_skill_w(mean_delta, draw_margin, c):
    team_performance_difference = mean_delta / c
    draw_margin = draw_margin / c
    denominator = gaussian.cdf(team_performance_difference - draw_margin)
    if denominator < 1e-161:
        if team_performance_difference < 0.0:
            return 1
        return 0

    v_win = true_skill_v(mean_delta*c, draw_margin*c, c)
    return v_win * (v_win + team_performance_difference - draw_margin)

def calculate_new_rating(own_rating, opponent_rating, won):
    draw_margin = get_draw_margin_from_draw_prob(DRAW_PROBABILITY, BETA)

    c = sqrt(own_rating.stddev**2 + opponent_rating.stddev**2 + 2*(BETA**2))

    if won:
        winning_mean, losing_mean = own_rating.mean, opponent_rating.mean
    else:
        winning_mean, losing_mean = opponent_rating.mean, own_rating.mean
    mean_delta = winning_mean - losing_mean

    v = true_skill_v(mean_delta, draw_margin, c)
    w = true_skill_w(mean_delta, draw_margin, c)
    rank_multiplier = 1 if won else -1

    variance_with_dynamics = own_rating.stddev**2 + DYNAMICS_FACTOR**2
    mean_multiplier = variance_with_dynamics/c
    stddev_multiplier = variance_with_dynamics/(c**2)

    new_mean = own_rating.mean + rank_multiplier*mean_multiplier*v
    new_stddev = sqrt(variance_with_dynamics*(max(1-w*stddev_multiplier, 0))) # FIXME: max here is wrong I think...

    return Rating(new_mean, new_stddev)


db = open('db.pkl')
teams = pickle.load(db)
games = pickle.load(db)
db.close()

ratings = {team : Rating(INITIAL_MEAN, INTIIAL_STDDEV) for team in teams}


for game in games.values():
    print
    print game
    
    winner = game.winner.espn_suffix
    loser  = game.loser.espn_suffix

    winner_prev_rating = ratings[winner]
    loser_prev_rating = ratings[loser]

    ratings[winner] = calculate_new_rating(winner_prev_rating, loser_prev_rating, True)
    ratings[loser]  = calculate_new_rating(loser_prev_rating, winner_prev_rating, False)

    print '%s: %s -> %s' % (game.winner, winner_prev_rating, ratings[winner])
    print '%s: %s -> %s' % (game.loser, loser_prev_rating, ratings[loser])


rankings = sorted([(teams[team].name, rating) for team, rating in ratings.iteritems()], key=lambda x: -x[1].conservative_rating())
for num, (name, rating) in enumerate(rankings):
    print '%s. %s [%s]' % (num+1, name, rating)

import code; code.interact(local=locals())

