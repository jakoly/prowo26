from pathlib import Path
import midi_api

# FIX 11: pathlib statt hardcodierter Windows-Pfade –
# Passe BASE_DIR auf dein Projektverzeichnis an.
BASE_DIR = Path(__file__).parent
INPUT_FILE  = BASE_DIR / "rasputin.mid"
OUTPUT_FILE = BASE_DIR / "rasputin_filtered.mid"


def main():
    midi_processor = midi_api.MidiProcessor()
    midi_processor.load_midi_file(INPUT_FILE)

    print("Filtering MIDI file...")
    print(
        f"Channel: {midi_processor.MIDI_CHANNEL + 1}, "
        f"Note range: {midi_processor.NOTE_RANGE[0]}-{midi_processor.NOTE_RANGE[1]}"
    )

    # FIX 12: Rückgabewert wird genutzt und in den Processor geladen,
    # damit play_midi_file() die gefilterte – nicht die originale – Version spielt.
    filtered = midi_processor.filter_midi_file(OUTPUT_FILE)
    if filtered is None:
        print("Filtering failed. Aborting.")
        return

    midi_processor.midi_file = filtered
    print(f"Filtered file saved to: {OUTPUT_FILE}")

    print("\nPlaying filtered file...")
    midi_processor.play_midi_file()


if __name__ == "__main__":
    main()