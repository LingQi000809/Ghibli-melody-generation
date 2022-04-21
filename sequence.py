#!/usr/local/bin/python3.7

import argparse
import os
import random

from Note import Note
from tidyup_coll import tidy_up


# tick of a quarter note
tick_quarter = 12
pitch_class = [0, 2, 3, 5, 7, 8, 10, 12]

def get_closest_inscale_tones(tone: int):
    if tone == 1:
        return [0, 2]
    elif tone == 4:
        return [3, 5]
    elif tone == 6:
        return [5, 7]
    elif tone == 9:
        return [8, 10]
    elif tone == 11:
        return [10, 12]


def main(args):
    coll_filepath = args.filepath
    coll_dirname = os.path.dirname(coll_filepath)
    coll_basename = os.path.basename(coll_filepath)

    start_idx = args.startindex
    end_idx = args.endindex

    endpitch = args.endpitch

    time_sig = args.timesig
    measure_tick = tick_quarter * time_sig
    default_dur = measure_tick

    notes = []

    # get the existing notes
    with open(coll_filepath, "r") as f:
        for line in f:
            # extract note info
            i, onset, pitch, dur, vel = line.strip().split()
            i = int(i[:-1])
            onset = int(onset)
            pitch = int(pitch)
            dur = int(dur)
            vel = int(vel[:-1])
            notes.append(Note(i, onset, pitch, dur, vel))

    offset = len(notes) - start_idx

    # sequencing
    notes_to_seq = notes[start_idx:end_idx]
    old_endpitch = notes_to_seq[-1].pitch
    interval = endpitch - old_endpitch

    for seq_i, note in enumerate(notes_to_seq):
        new_idx = note.index + offset
        # since the rest in a statement can only be at the beginning,
        # we simply remove the rest, so that we would extend the last note during tidy-up
        if note.dur < 0:
            offset -= 1
            continue
        
        # change pitch level
        if note.pitch > 0:
            last_pitch_original = notes_to_seq[seq_i-1].pitch
            if seq_i == 0 or last_pitch_original <= 0:
                new_pitch = note.pitch + interval
            else:
                new_pitch = note.pitch - last_pitch_original + notes[-1].pitch
            note_tone = new_pitch % 12
            register = int(new_pitch / 12)

            # deal with out-of-scale tones => diatonic transposition
            if note_tone not in pitch_class:
                alt_tones = get_closest_inscale_tones(note_tone)

                if seq_i == 0:
                    new_tone = random.choice(alt_tones)
                    # first note in seq should not be the same as the original first note 
                    if new_tone + register * 12 == note.pitch:
                        alt_tones.remove(new_tone)
                        new_tone = alt_tones[0]
                    new_pitch = new_tone + register * 12

                # not first note: decide the alt note to pick based on the direction from last note
                else: 
                    last_pitch = notes[-1].pitch
                    # alt_tones is always from smaller pitch to larger one
                    # we want to maintain the melodic contour, 
                    # so we pick the alt_note with the original direction relative to the previous pitch
                    if last_pitch < new_pitch:
                        new_tone = alt_tones[1]
                    else:
                        new_tone = alt_tones[0]
                    new_pitch = new_tone + register * 12

        else: 
            new_pitch = note.pitch
        
        seq_note = Note(new_idx, note.onset, new_pitch, note.dur, note.vel)
        notes.append(seq_note)

    # output file
    with open(coll_filepath, "w") as f:
            for note in notes:
                f.write(f"{note.index}, {note.onset} {note.pitch} {note.dur} {note.vel};\n")

    # tidy up the collection from the note before the added repetition
    tidy_up(coll_filepath, end_idx - 1, args.timesig, coll_basename="rand_coll")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath",
        type=str,
        help="path to the collection file"
    )
    parser.add_argument(
        "startindex",
        type=int,
        help="the starting index (inclusive) of the statement for the sequence"
    )
    parser.add_argument(
        "endindex",
        type=int,
        help="the ending index (exclusive) of the statement for the sequence"
    )
    parser.add_argument(
        "endpitch",
        type=int,
        help="the new ending note of the sequence"
    )
    parser.add_argument(
        "timesig",
        type=int,
        help="the time signature beat count"
    )

    args = parser.parse_args()
    main(args)