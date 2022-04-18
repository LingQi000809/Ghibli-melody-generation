#!/usr/local/bin/python3.7

import argparse
import json
import os
import numpy as np

num_pitches = 108
tick_quarter = 12
num_onsets = tick_quarter * 4

class Markov:
    def __init__(self, num_states: int):
        # [
        #     [1 0 2], state 0's count of transition to each state
        #     [2 3 1], state 1's count of transition to each state
        #     [1 0 0]  state 2's count of transition to each state
        # ]
        self.num_states = num_states
        self.transition_count = np.zeros((num_states, num_states))
        # count of each state being the initial state
        self.init_count = [0 for n in range (num_states)]
        self.num_Tunes = 0

    def add_transitions(self, seq: list):
        # add the transition counts
        last = 0
        for i, num in enumerate(seq):
            if i == 0:
                # starting with
                self.init_count[num] += 1
            else:
                # last -> num: 1 more occurence
                self.transition_count[last][num] += 1
            last = num
        self.num_Tunes += 1
    
    def write_transitions(self, to_fname: str):
        with open(to_fname, "w") as pf:
            # reset, states, build
            pf.write(f"reset\nstates {self.num_states}\nbuild")
            # initial prob
            pf.write("\ninitial_prob 0")
            for count in self.init_count[:-1]:
                prob = count / self.num_Tunes
                pf.write(f" {prob}")
            # transitions
            for i, state in enumerate(self.transition_count):
                # no transition for the state if all zero
                if not state.any():
                    continue
                pf.write(f"\ntransitions {i}")
                total = np.sum(state)
                for count in state:
                    prob = count / total
                    pf.write(f" {prob}")

def main(args):
    mood = args.mood
    isMajor = args.mode == "major"
    mode = "+" if isMajor else "-"
    timesig = args.timesig

    coll_dir = "midi_coll"

    # initialize pitch and onset markovs
    pitch_markov = Markov(num_pitches)
    onset_markov = Markov(num_onsets)

    # go through the midi directory
    files = os.listdir(os.path.join(coll_dir,mood))
    for f in files:
        # look at valid txt files
        if f.endswith('.txt') and not f.startswith('.'):
            # from the file name, extract the mode and time signature info
            fname = os.path.splitext(f)[0]
            fmode = fname[-2]
            ftime = int(fname[-1])
            # look at tunes with the wanted mode and timesig
            if mode == fmode and timesig == ftime:
                print(f"{f}")
                pitches = []
                onsets = []
                # add transitions for pitch and onset to the corresponding markov
                with open(os.path.join(coll_dir, mood, f)) as rf:
                    for line in rf:
                        props = line.split()
                        onset = int(props[1])
                        pitch = int(props[2])
                        onsets.append(onset)
                        pitches.append(pitch)
                pitch_markov.add_transitions(pitches)
                onset_markov.add_transitions(onsets)
    # after adding transitions from each file of the wanted categories, output the transition table
    pitch_markov.write_transitions("pitch_markov.txt")
    onset_markov.write_transitions("onset_markov.txt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mood",
        type=str,
        help="mood category"
    )
    parser.add_argument(
        "--mode",
        type=str,
        help="major or minor mode"
    )
    parser.add_argument(
        "--timesig",
        type=int,
        help="the time signature beat count"
    )

    args = parser.parse_args()
    main(args)