#!/usr/local/bin/python3.7

import argparse
import os

from Note import Note
from tidyup_coll import tidy_up


# tick of a quarter note
tick_quarter = 12


def main(args):
    coll_filepath = args.filepath
    coll_dirname = os.path.dirname(coll_filepath)
    coll_basename = os.path.basename(coll_filepath)

    start_idx = args.startindex
    end_idx = args.endindex

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

    # repeat notes
    notes_to_repeat = notes[start_idx:end_idx]
    for note in notes_to_repeat:
        new_idx = note.index + offset
        # since the rest in a statement can only be at the beginning,
        # we simply remove the rest, so that we would extend the last note during tidy-up
        if note.dur < 0:
            offset -= 1
            continue
        rep_note = Note(new_idx, note.onset, note.pitch, note.dur, note.vel)
        notes.append(rep_note)

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
        help="the starting index (inclusive) of the statement to repeat"
    )
    parser.add_argument(
        "endindex",
        type=int,
        help="the ending index (exclusive) of the statement to repeat"
    )
    parser.add_argument(
        "timesig",
        type=int,
        help="the time signature beat count"
    )

    args = parser.parse_args()
    main(args)