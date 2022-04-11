#!/usr/local/bin/python3.7

import argparse
import os

from Note import Note

# tick of a quarter note
tick_quarter = 12
measure_tick = tick_quarter * 4 # 48
default_dur = measure_tick

def tidy_up(coll_filepath: str, start_idx: int, 
    coll_basename: str = None):
    coll_dirname = os.path.dirname(coll_filepath)
    if not coll_basename:
        coll_basename = os.path.basename(coll_filepath)
    tidy_filepath = os.path.join(coll_dirname, f"tidy_{coll_basename}")
    group_filepath = os.path.join(coll_dirname, f"group_{coll_basename}")

    with open(coll_filepath, "r") as rf:
        tidy_notes = []
        groups = []
        group_num = 0
        index_offset = 0

        # calculate durations, add rests & ties, and group notes
        for line in rf:
            # extract note info
            i, onset, pitch, dur, vel = line.strip().split()
            i = int(i[:-1])
            onset = int(onset)
            pitch = int(pitch)
            dur = int(dur)
            vel = int(vel[:-1])

            # for already tidy-ed note (from last tidyup)
            if i < start_idx:
                if tidy_notes and onset == 0:
                    groups.append(group_num)
                    group_num = 0 
                note = Note(i + index_offset, onset, pitch, dur, vel)
                tidy_notes.append(note)
                group_num += 1
                continue

            # if we have a last note...
            if tidy_notes:
                last_note = tidy_notes[i + index_offset -1]
                last_onset = last_note.onset
                # condition 1: new measure; no carry-over
                if onset == 0:
                    # 1) last note dur
                    if last_note.dur > 0:
                        last_note.update_dur(measure_tick - last_onset)
                    # 2) group last measure
                    groups.append(group_num)
                    group_num = 0

                # condition 2 (TIE): new measure; carry-over
                elif onset <= last_onset:
                    if last_note.dur > 0:
                        # 1) last note dur in last measure
                        last_note.update_dur(measure_tick - last_onset)
                        # 2) new note 1: tie (last measure)
                        tidy_notes.append(Note(i + index_offset, default_dur, 0, 0, 0))
                        index_offset += 1
                        # 3) new note 2: last note carry-over dur to this measure (this measure)
                        tidy_notes.append(Note(i + index_offset , 0, last_note.pitch, onset, last_note.vel))
                        index_offset += 1
                    else:
                        # last note was a rest in the previous measure
                        # we should add a rest in front of the current note (as its onset is not 0)
                        tidy_notes.append(Note(i + index_offset, 0, 0, -1 * onset, 0))
                        index_offset += 1
                    # group last measure (add 1 for the tie)
                    groups.append(group_num + 1)
                    # reset group_num to 1 because of the added carry-over note / rest
                    group_num = 1

                # condition 3: same measure
                else: # onset > last_onset
                    # just update the dur of last note
                    if last_note.dur > 0:
                        last_note.update_dur(onset - last_onset)
            
            # if this is the first note...
            else:
                # add rests at the start
                if onset != 0:
                    # 1) add rest (negative dur)
                    tidy_notes.append(Note(0, 0, 0, onset * -1, 0))
                    index_offset += 1
                    # 2) reset group_num to 1 because of the added rest
                    group_num = 1

            # add current note to list
            note = Note(i + index_offset, onset, pitch, measure_tick, vel)
            tidy_notes.append(note)
            group_num += 1

        # update last note's duration
        if tidy_notes:
            final_note = tidy_notes[-1]
            final_note.update_dur(measure_tick - final_note.onset)
            groups.append(group_num)

        # TODO: RESTS

        print(groups)

        with open(tidy_filepath, "w") as f:
            for note in tidy_notes:
                f.write(f"{note.index}, {note.onset} {note.pitch} {note.dur} {note.vel};\n")
        with open(group_filepath, "w") as f:
            for i, num in enumerate(groups):
                f.write(f"{i}, {num};\n")


def main(args):
    coll_filepath = args.filepath
    start_idx = args.startindex
    tidy_up(coll_filepath, start_idx)

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filepath",
        type=str,
        help="path to the collection file to tidy up"
    )
    parser.add_argument(
        "startindex",
        type=int,
        help="the starting index of the statement to tidy up"
    )

    args = parser.parse_args()
    main(args)