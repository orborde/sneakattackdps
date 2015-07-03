/*
	Determine whether Jimmy Worther is better off constantly hiding,
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
*/


#include <assert.h>
#include <iostream>
#include <map>
#include <random>
#include <string>
#include <unordered_set>

using namespace std;

#define REPV(v, ct) for(long v=0; v < ct; v++)
#define REP(ct) REPV(i, ct)

const bool VERBOSE = false;

std::random_device rd;
std::mt19937 mt(rd());

int d(int n) {
	std::uniform_int_distribution<int> dist(1, n);
	return dist(mt);
}

// State machine constants
enum combatstate {
	MT,
	L,
	LH
};

enum combataction {
	LOAD,
	ATK,
	HIDE
};

string name(const combatstate state) {
	switch(state) {
	case MT: return "MT";
	case L:  return "L";
	case LH: return "LH";
	}

	assert(0);
	return "wtf";
}

string name(const combataction action) {
	switch(action) {
	case LOAD: return "LOAD";
	case ATK:  return "ATK";
	case HIDE: return "HIDE";
	}

	assert(0);
	return "wtf";
}


// Strategy implementations
typedef combataction(*strategy)(combatstate);

combataction ATK_STRAT(const combatstate state) {
	switch(state) {
	case MT: return LOAD;
	case L:  return ATK;
	case LH: break;
	}

	assert(0);
}

combataction SNEAK_STRAT(const combatstate state) {
	switch(state) {
	case MT: return LOAD;
	case L:  return HIDE;
	case LH: return ATK;
	}
	assert(0);
}

// Stats
const int ATK_BONUS = 8;
const int ENEMY_AC = 17; // Roll + attack bonus must reach this to hit.
const int HIDE_MIN = 11; /* Roll required to successfully hide (p = 1/2 for
														approximation) */

int BOLT_DMG() {
	return 1 + d(8);
}

int SNEAK_DMG() {
	return BOLT_DMG() + d(6) + d(6);
}

const int CRIT_MIN = 19;
const int CRIT_MUL = 2;

const long ITER_COUNT = 10000000;

enum attack_outcome {
	MISS,
	HIT,
	CRIT
};

string name(attack_outcome outcome) {
	switch(outcome) {
	case MISS: return "MISS";
	case HIT:  return "HIT";
	case CRIT: return "CRIT";
	}

	assert(0);
	return "wtf";
}

attack_outcome attack_roll(const bool verbose = VERBOSE) {
	const auto roll = d(20);

	if (roll >= CRIT_MIN) {
		if (verbose) { cout << "CRITICAL on " << roll << endl; };
		return CRIT;
	}

	const auto mod_roll = roll + ATK_BONUS;
	if (mod_roll >= ENEMY_AC) {
		if (verbose) {
			cout << "HIT on " << roll << " + " << ATK_BONUS
					 << " = " << mod_roll << endl;
		}
		return HIT;
	}

	if (verbose) {
		cout << "MISS on " << roll << " + " << ATK_BONUS
				 << " = " << mod_roll << endl;
	}
	return MISS;
}

int attack_roll_dmg(int (*damage_func)(void), const bool verbose=VERBOSE) {
	const auto outcome = attack_roll(verbose);
	if (outcome == HIT) {
		const auto dmg = damage_func();
		if (verbose) { cout << dmg << " damage" << endl; }
		return dmg;
	}

	if (outcome == CRIT) {
		const auto dmg = CRIT_MUL * damage_func();
		if (verbose) { cout << dmg << " damage" << endl; }
		return dmg;
	}

  assert(outcome == MISS);
	return 0;
}


void run_round(const combatstate state, strategy strat,
							 combatstate* const newstate, int* const dmg) {

	combataction action = strat(state);
	if (VERBOSE) {
		cout << "On " << name(state)	
				 << " / choosing " << name(action) << endl;
	}

	switch(state) {
	case MT:
		if (action == LOAD) {
				*newstate = L;
				*dmg = 0;
				return;
			}
		assert(0);

	case L:
		if (action == ATK) {
			*newstate = MT;
			*dmg = attack_roll_dmg(BOLT_DMG);
			return;
		}

		if (action == HIDE) {
			if (d(20) >= HIDE_MIN) {
				*newstate = LH;
				*dmg = 0;
				return;
			} else {
				*newstate = L;
				*dmg = 0;
				return;
			}
		}
		assert(0);

	case LH:
		if (action == ATK) {
			if (VERBOSE) { cout << "SNEAK ATTACK!" << endl; }
			*newstate = MT;
			*dmg = attack_roll_dmg(SNEAK_DMG);
			return;
		}
		assert(0);
	default:
		assert(0);
	}
}


float eval_strat(strategy strat, const long iters=ITER_COUNT) {
	combatstate state = MT;
	long dmg = 0;

	if (VERBOSE) { cout << "START: " << state << dmg << endl; }
	REP(iters) {
		combatstate newstate;
		int dmginc;
		run_round(state, strat, &newstate, &dmginc);
		state = newstate;
		dmg += dmginc;
		if (VERBOSE) { cout << "STEP " << i << " : " << state << dmg << endl; }
	}

	return float(dmg) / iters;
}

int main() {
	float Da, Dsa;
	{
    long bd = 0;
    long sd = 0;

		REP(ITER_COUNT) {
			bd += BOLT_DMG();
			sd += SNEAK_DMG();
		}

    Da = float(bd) / ITER_COUNT;
		Dsa = float(sd) / ITER_COUNT;
	}

	cout << "BOLT dmg/hit (Da): " << Da << " (exp 5.5)" << endl;
	cout << "SNEAK dmg/hit (Dsa): " << Dsa << " (exp 12.5)" << endl;

	float ph;
	{
    int hits = 0;
		REP(ITER_COUNT) {
			const auto res = attack_roll(false);
			if (res == HIT or res == CRIT ) hits++;
			ph = float(hits) / ITER_COUNT;
		}
	}
	cout << "Ph ~= " << ph << endl;

	{
		long sum = 0;
		REP(ITER_COUNT) { sum += attack_roll_dmg(SNEAK_DMG, false); }

		cout << "D(LH) / Dsa ~= "
				 << (float(sum) / ITER_COUNT / Dsa) << endl;
	}

	float atk_dmg = eval_strat(ATK_STRAT);
	cout << "Standard dmg/action: " << atk_dmg
			 << " (exp 1.925/action)" << endl;
	float sneak_dmg = eval_strat(SNEAK_STRAT);
	cout << "Sneak attack dmg/action: " << sneak_dmg
			 << " (exp 2.1875/action)" << endl;

	return 0;
}

