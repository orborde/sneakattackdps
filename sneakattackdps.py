"""Determine whether Jimmy Worther is better off constantly hiding,
then sneak attacking, or simply making regular attacks. At least, in
DPS terms.

Rules are:
2 actions per round

Each action, you can make a choice about what to do, resulting in
(maybe) the another state.

STATES:
MT - "Empty" - Crossbow not loaded. Not hidden. Initial state.
--> L  : Can load crossbow

L - "Loaded" - Crossbow loaded
--> MT : Can make a normal attack roll, which empties the crossbow.
--> LH : Can attempt to hide (takes a check)

LH - "Loaded + Hidden" - Crossbow loaded, and successfully hidden.
--> MT : Can make a sneak attack roll, which empties the crossbow
         and drops hiding.
"""

import random

def dN(n):
    return random.randint(1, n)
d4 = lambda: dN(4)
d6 = lambda: dN(6)
d8 = lambda: dN(8)
d10 = lambda: dN(10)
d20 = lambda: dN(20)

MT = "MT"
L  = "L"
LH = "LH"

ATK_BONUS = 8
ENEMY_AC = 17  # Roll + attack bonus must reach this to hit.

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
