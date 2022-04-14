class Note:
    def __init__(self, index: int, onset: int, pitch: int, dur: int, vel: int):
        self.index = index
        self.onset = onset
        self.pitch = pitch
        self.dur = dur
        self.vel = vel

    def update_pitch(self, new_pitch: int):
        self.pitch = new_pitch

    def update_dur(self, new_dur: int):
        self.dur = new_dur

