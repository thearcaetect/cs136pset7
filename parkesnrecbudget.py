#!/usr/bin/env python

import sys

from gsp import GSP
import math
from util import argmax_index

class Parkesnrecbudget:
    """Balanced bidding agent"""
    def __init__(self, id, value, budget):
        self.id = id
        self.value = value
        self.budget = budget

    def initial_bid(self, reserve):
        return self.value / 2


    def slot_info(self, t, history, reserve):
        """Compute the following for each slot, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns list of tuples [(slot_id, min_bid, max_bid)], where
        min_bid is the bid needed to tie the other-agent bid for that slot
        in the last round.  If slot_id = 0, max_bid is 2* min_bid.
        Otherwise, it's the next highest min_bid (so bidding between min_bid
        and max_bid would result in ending up in that slot)
        """
        prev_round = history.round(t-1)
        other_bids = filter(lambda (a_id, b): a_id != self.id, prev_round.bids)

        clicks = prev_round.clicks
        def compute(s):
            (min, max) = GSP.bid_range_for_slot(s, clicks, reserve, other_bids)
            if max == None:
                max = 2 * min
            return (s, min, max)
            
        info = map(compute, range(len(clicks)))
#        sys.stdout.write("slot info: %s\n" % info)
        return info


    def expected_utils(self, t, history, reserve):
        """
        Figure out the expected utility of bidding such that we win each
        slot, assuming that everyone else keeps their bids constant from
        the previous round.

        returns a list of utilities per slot.
        """
        # TODO: Fill this in
        info = self.slot_info(t, history, reserve)
        num_clicks = (history.round(t-1)).clicks
        # print info
        # CHECK: DO WE NEED THIS??
        # c_1 = round(30 * math.cos(math.pi * t / 24) + 50)
        utilities = []
        for j in range(len(info)):
            v_i = self.value
            t_j = info[j][1]
            utilities.append(num_clicks[j] * (v_i - t_j))
        return utilities

    def target_slot(self, t, history, reserve):
        """Figure out the best slot to target, assuming that everyone else
        keeps their bids constant from the previous rounds.

        Returns (slot_id, min_bid, max_bid), where min_bid is the bid needed to tie
        the other-agent bid for that slot in the last round.  If slot_id = 0,
        max_bid is min_bid * 2
        """
        i = argmax_index(self.expected_utils(t, history, reserve))
        info = self.slot_info(t, history, reserve)
        return info[i]


    def linear_scale(self, val, bottom_val=100, top_val=175, top_scale=0.5):
        # val is the agent's current value
        # bottom val is the lower bound where we do not scale the bid
        # top val is the highest possible value
        # top scale is the value we scale the bid down by if the agent's value
        # is the maximum value
        pct_range = (float(val) - bottom_val) / (top_val - bottom_val)
        # print val
        # print pct_range
        # print 1.0 - (top_scale * pct_range)
        return (1.0 - (top_scale * pct_range))

    def bid(self, t, history, reserve):
        # The Balanced bidding strategy (BB) is the strategy for a player j that, given
        # bids b_{-j},
        # - targets the slot s*_j which maximizes his utility, that is,
        # s*_j = argmax_s {clicks_s (v_j - t_s(j))}.
        # - chooses his bid b' for the next round so as to
        # satisfy the following equation:
        # clicks_{s*_j} (v_j - t_{s*_j}(j)) = clicks_{s*_j-1}(v_j - b')
        # (p_x is the price/click in slot x)
        # If s*_j is the top slot, bid the value v_j

        prev_round = history.round(t-1)
        (slot, min_bid, max_bid) = self.target_slot(t, history, reserve)
        if min_bid > self.value or slot == 0:
            bid = self.value
        # QUESTION: is t_j same as min_bid?????
        else:
            num_clicks = (history.round(t-1)).clicks
            ctr_ratio = float(num_clicks[slot]) / float(num_clicks[slot - 1])
            bid = self.value - ctr_ratio * (self.value - min_bid)

        lower_scale_bound = 130
        # print 'VALL'
        # print self.value
        # print 'KANYE'
        if self.value >= lower_scale_bound:
            return bid * self.linear_scale(self.value, bottom_val=lower_scale_bound)
        else:
            return bid


    def __repr__(self):
        return "%s(id=%d, value=%d)" % (
            self.__class__.__name__, self.id, self.value)


