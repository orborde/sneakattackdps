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
    print 'BOLT dmg/hit:', float(bd) / ITER_COUNT, '(exp 5.5)'
    print 'SNEAK dmg/hit:', float(sd) / ITER_COUNT, '(exp 12.5)'
hit_dps()

MISS = "MISS"
HIT = "HIT"
CRIT = "CRIT"
def attack_roll():
    roll = d20()
    if roll >= CRIT_MIN:
        return CRIT
    if roll + ATK_BONUS >= ENEMY_AC:
        return HIT
    return MISS


def attack_roll_dmg(damage_func):
    outcome = attack_roll()
    if outcome is HIT:
        return damage_func()
    if outcome is CRIT:
        return CRIT_MUL * damage_func()
    assert outcome is MISS
    return 0


def run_round(state, strat):
    """Returns (newstate, damage_done) tuple."""
    action = strat[state]

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

