"""Determine whether Jimmy Worther is better off constantly hiding,
then sneak attacking, or simply making regular attacks. At least, in
DPS terms.

Rules are:
2 actions per round

Each action, you can make a choice about what to do, resulting in
(maybe) the another state.

STATES:
MT - "Empty" - Crossbow not loaded. Not hidden. Initial state.
 LOAD --> L  : Can load crossbow

L - "Loaded" - Crossbow loaded
 ATK  --> MT : Can make a normal attack roll, which empties the crossbow.
 HIDE --> LH : Can attempt to hide (takes a check)

LH - "Loaded + Hidden" - Crossbow loaded, and successfully hidden.
 ATK  --> MT : Can make a sneak attack roll, which empties the
               crossbow and drops hiding.
"""

import random

VERBOSE = True

def dN(n):
    return random.randint(1, n)
d4 = lambda: dN(4)
d6 = lambda: dN(6)
d8 = lambda: dN(8)
d10 = lambda: dN(10)
d20 = lambda: dN(20)

# State machine constants
MT = "MT"
L  = "L"
LH = "LH"
LOAD = "LOAD"
ATK = "ATK"
HIDE = "HIDE"

# Strategy implementations
ATK_STRAT = {
    MT : LOAD,
    L  : ATK
}

SNEAK_STRAT = {
    MT : LOAD,
    L  : HIDE,
    LH : ATK
}

# Stats
ATK_BONUS = 8
ENEMY_AC = 17  # Roll + attack bonus must reach this to hit.

HIDE_MIN = 11  # Roll required to successfully hide (p = 1/2 for
               # approximation)

BOLT_DMG = lambda: 1 + d8()
SNEAK_DMG = lambda: BOLT_DMG() + d6() + d6()

CRIT_MIN = 19
CRIT_MUL = 2

ITER_COUNT = 10000

def hit_dps():
    bd = 0
    sd = 0
    for i in range(ITER_COUNT):
        bd += BOLT_DMG()
        sd += SNEAK_DMG()
    return float(bd) / ITER_COUNT, float(sd) / ITER_COUNT
Da, Dsa = hit_dps()
print 'BOLT dmg/hit (Da):', Da, '(exp 5.5)'
print 'SNEAK dmg/hit (Dsa):', Dsa, '(exp 12.5)'

MISS = "MISS"
HIT = "HIT"
CRIT = "CRIT"
def attack_roll(VERBOSE=VERBOSE):
    roll = d20()
    if roll >= CRIT_MIN:
        if VERBOSE: print 'CRITICAL on', roll
        return CRIT

    mod_roll = roll + ATK_BONUS
    if mod_roll >= ENEMY_AC:
        if VERBOSE:
            print 'HIT on', roll, '+', ATK_BONUS, '=', mod_roll
        return HIT

    if VERBOSE: print 'MISS on', roll, '+', ATK_BONUS, '=', mod_roll
    return MISS


def ph():
    hits = 0
    for i in range(ITER_COUNT):
        res = attack_roll(VERBOSE=False)
        if res is HIT or res is CRIT:
            hits += 1
    return float(hits) / ITER_COUNT
print 'Ph ~=', ph()


def attack_roll_dmg(damage_func, VERBOSE=VERBOSE):
    outcome = attack_roll(VERBOSE=VERBOSE)
    if outcome is HIT:
        dmg = damage_func()
        if VERBOSE: print dmg, 'damage'
        return dmg
    if outcome is CRIT:
        dmg = CRIT_MUL * damage_func()
        if VERBOSE: print dmg, 'damage'
        return dmg
    assert outcome is MISS
    return 0


print 'D(LH) / Dsa ~=',
print (float(sum(
    attack_roll_dmg(SNEAK_DMG, VERBOSE=False) for i in range(ITER_COUNT)))
       /
       ITER_COUNT
       /
       Dsa)


def run_round(state, strat):
    """Returns (newstate, damage_done) tuple."""
    action = strat[state]
    if VERBOSE: print "On", state, "/ choosing", action

    if state is MT:
        if action is LOAD:
            return L, 0
        assert False

    if state is L:
        if action is ATK:
            return MT, attack_roll_dmg(BOLT_DMG)
        if action is HIDE:
            if d20() >= HIDE_MIN:
                return LH, 0
            else:
                return L, 0
        assert False

    if state is LH:
        if action is ATK:
            return MT, attack_roll_dmg(SNEAK_DMG)
        assert False

    assert False


def eval_strat(strat, iters=ITER_COUNT):
    state, dmg = MT, 0
    for i in range(iters):
        state, dmginc = run_round(state, strat)
        dmg += dmginc
    return float(dmg) / iters

print 'Standard dmg/action:', eval_strat(ATK_STRAT)
print 'Sneak attack dmg/action:', eval_strat(SNEAK_STRAT)

