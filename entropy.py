
from constants import *
import probability_assignment
import sat_model
from math import log
from pyeda.inter import *

# Given rules and open tiles (see probability_assignment.py), computes an entropy map from (x, y) to information gain.
# Each coordinate is mapped to a value from 0 to 1 describing how much information can be gained from opening up that
# tile.
def entropy_map(col_rules, row_rules, open_tiles = dict()):
    em = dict()

    base_formula = sat_model.setup_formula(col_rules, row_rules)
    ot_formula = sat_model.setup_known(open_tiles)
    pre_f = And(base_formula, ot_formula).tseitin()
    pre_pa = probability_assignment.compute_probass(pre_f)

    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            ig_sum = 0
            if (x, y) not in open_tiles:
                for v in range(MAX_VAL+1):
                    if pre_pa[(x, y, v)] > 0:
                        post_f = And(pre_f, sat_model.setup_known({(x, y): v})).tseitin()
                        post_pa = probability_assignment.compute_probass(post_f)
                        ig_sum += information_gain(pre_pa, post_pa) * pre_pa[(x, y, v)]
            em[(x, y)] = ig_sum
    return em


# For probability assignments for "before" and "after", computes the information gain.
def information_gain(pre_pa, post_pa):
    pre_ig = 0
    post_ig = 0
    for x in range(FIELD_SIZE):
        for y in range(FIELD_SIZE):
            for v in range(MAX_VAL+1):
                pre_ig += etp(pre_pa[(x, y, v)])
                post_ig += etp(post_pa[(x, y, v)])
    return (pre_ig - post_ig) / (FIELD_SIZE * FIELD_SIZE)


def etp(x):
    if x == 0 or x == 1:
        return 0
    else:
        return -x * log(x, 2)