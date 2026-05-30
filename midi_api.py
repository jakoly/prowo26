import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import time


# FIX 4: snake_case nach PEP 8
def is_valid_note(msg, midi_channel=0, note_range=(48, 84)):
    """Check if message is a valid note in the configured range and channel."""
    return (
        msg.type in ["note_on", "note_off"]
        and msg.channel == midi_channel
        and note_range[0] <= msg.note <= note_range[1]
    )


def to_note_value(note_str: str) -> int:
    """Convert note string (e.g. 'C3') to MIDI note number (e.g. 48)."""
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_name = note_str[:-1]
    octave = int(note_str[-1])
    return note_names.index(note_name) + (octave + 1) * 12


class MidiProcessor:
    # FIX 5: Einrückung auf 4 Leerzeichen korrigiert
    def __init__(self, channel=0, note_range=(to_note_value("C3"), to_note_value("C8"))):
        self.MIDI_CHANNEL = channel
        self.NOTE_RANGE = note_range
        self.midi_file = None

        try:
            mido.set_backend("mido.backends.rtmidi", load=True)
        except ImportError:
            # FIX 3: Korrekte pip-Anleitung
            print("Backend not found. Please run 'pip install -r requirements.txt' to install the required dependencies.")

    def load_midi_file(self, input_path: str):
        """Load a MIDI file from disk."""
        self.midi_file = MidiFile(input_path)

    def filter_midi_file(self, output_path=None):
        """Remove out-of-range notes and save the filtered MIDI file."""
        # FIX 1: Docstring steht jetzt korrekt am Anfang der Methode
        if not self.midi_file:
            print("No MIDI file loaded. Please load a MIDI file before attempting to filter.")
            return None

        filtered_file = MidiFile(ticks_per_beat=self.midi_file.ticks_per_beat)

        for track in self.midi_file.tracks:
            filtered_track = MidiTrack()
            accumulated_time = 0

            for msg in track:
                if msg.type not in ["note_on", "note_off"]:
                    new_msg = msg.copy(time=msg.time + accumulated_time)
                    filtered_track.append(new_msg)
                    accumulated_time = 0
                elif is_valid_note(msg, self.MIDI_CHANNEL, self.NOTE_RANGE):
                    new_msg = msg.copy(time=msg.time + accumulated_time)
                    filtered_track.append(new_msg)
                    accumulated_time = 0
                else:
                    accumulated_time += msg.time

            filtered_file.tracks.append(filtered_track)

        if output_path:
            filtered_file.save(output_path)
        return filtered_file

    def play_midi_file(self):
        """Play the loaded MIDI file with proper timing."""
        if self.midi_file is None:
            print("No MIDI file loaded. Please load a MIDI file before attempting to play.")
            return

        try:
            start_time = time.time()

            for msg in self.midi_file.play():
                # FIX 2: time.sleep() entfernt – mido.play() handhabt Timing intern
                if not msg.is_meta:
                    print(f"Playing: {msg}")

            elapsed = time.time() - start_time
            print(f"Finished playing MIDI file. Total time: {elapsed:.2f} seconds")

        except (AttributeError, OSError) as e:
            print(f"Error while attempting to play MIDI file: {e}")