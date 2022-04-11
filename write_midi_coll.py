#!/usr/local/bin/python3.7

import argparse
import json
import os

from music21 import *

# tick of a quarter note
tick_quarter = 12

def normalize_score(score: stream.Score):
    """ normalize all major key to E-, and all minor key to Cm """

def get_onset_tick(note: note.Note) -> int:
    # 1 => first beat => onset = 0 (smallest value)
    # 1 1/2 => dotted after first beat => onset = 6
    # 2 1/3 => triplet after second beat => onset = 16
    beatstr = note.beatStr
    onsets = beatstr.split()
    full_onset = (int(onsets[0]) - 1) * tick_quarter
    if len(onsets) == 2:
        rest_onset_fraction = onsets[1].split('/')
        numerator = int(rest_onset_fraction[0])
        denominator = int(rest_onset_fraction[1])
        rest_onset = int((numerator * tick_quarter) / denominator)
    else:
        rest_onset = 0
    return full_onset + rest_onset

def parse_file(midi_file: str, coll_dir: str = "midi_coll", normalize_key: bool = True):
    # extract file name without path or extension
    dirname = os.path.dirname(midi_file)
    mood_dir_name = os.path.basename(dirname)
    name = os.path.splitext(os.path.basename(midi_file))[0]
    coll_fp = os.path.join(coll_dir, mood_dir_name, name) + ".txt"

        
    score = converter.parse(midi_file, format='midi', quarterLengthDivisors=[12,16])
    if normalize_key:
        normalize_score(score)
    score = score.flatten()

    for t in score.getElementsByClass(meter.TimeSignature):
        num_beats = t.numerator
        beat_length = t.denominator
        print(f'Time signature: {num_beats}/{beat_length}')
        if beat_length != 4:
            print(f'This program only supports beat length of 4 for now. Discarded.')
            return

    with open(coll_fp, "w") as wf:
        notes = score.notes
        note_i = -1
        for i, note in enumerate(notes):
            # onset in the current measure
            onset = get_onset_tick(note)
            # discard tied-over notes
            if onset == 0 and note.tie and note.tie.type == 'stop':
                continue
            # midi num
            midi_num = note.pitch.midi
            # NOTE: dur not of interest for now 
            dur = 100
            # vel
            vel = note.volume.velocity
            # coll index
            note_i += 1
            # write to file in Max coll format
            wf.write(f"{note_i}, {onset} {midi_num} {dur} {vel};\n")

def main(args):
    midi_file = args.midifile
    midi_folder = args.midifolder

    coll_dir = "midi_coll"

    if midi_file:
        parse_file(midi_file)
    
    if midi_folder:
        for dir_name in os.listdir(midi_folder):
            if dir_name.startswith('.'):
                continue
            coll_dir_path = os.path.join(coll_dir, dir_name)
            if not os.path.exists(coll_dir_path):
                os.mkdir(coll_dir_path)
            for file_name in os.listdir(os.path.join(midi_folder, dir_name)):
                if file_name.startswith('.'):
                    continue
                fp = os.path.join(midi_folder, dir_name, file_name)
                print(fp)
                parse_file(fp, coll_dir=coll_dir)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a midi file into Tone.js-friendly JSON format at: https://tonejs.github.io/Midi/")
    parser.add_argument(
        "--midifile",
        type=str,
        help="path to a midi file. "
    )
    parser.add_argument(
        "--midifolder",
        type=str,
        help="path to a folder that contains midi files."
    )

    args = parser.parse_args()
    main(args)