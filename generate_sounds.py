import wave
import math
import random
import struct
import os
from pathlib import Path

# Setup Paths
ASSET_DIR = Path("assets/sounds")
ASSET_DIR.mkdir(parents=True, exist_ok=True)


def write_wav(filename, data):
    with wave.open(str(ASSET_DIR / filename), 'w') as f:
        f.setnchannels(1)  # Mono
        f.setsampwidth(2)  # 2 bytes per sample (16-bit)
        f.setframerate(44100)
        f.writeframes(data)
    print(f"Generated: {filename}")


def generate_steam_hiss(duration=0.1):
    """Base Tower: Short, sharp hiss."""
    data = bytearray()
    for i in range(int(44100 * duration)):
        noise = random.uniform(-1, 1)
        envelope = 1.0 - (i / (44100 * duration))
        sample = int(noise * envelope * 32767 * 0.5)
        data.extend(struct.pack('<h', sample))
    return data


def generate_thud(duration=0.3):
    """AOE Tower: Deep mechanical thud."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        freq = 150 * (1 - (i / samples))
        value = math.sin(2 * math.pi * freq * t)
        noise = random.uniform(-0.2, 0.2)
        envelope = 1.0 - (i / samples) ** 2
        sample = int((value + noise) * envelope * 32767 * 0.8)
        data.extend(struct.pack('<h', sample))
    return data


def generate_clang(duration=0.5):
    """UI: Metallic construction sound."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        v1 = math.sin(2 * math.pi * 440 * t)
        v2 = math.sin(2 * math.pi * 550 * t)
        v3 = math.sin(2 * math.pi * 880 * t)
        value = (v1 + v2 + v3) / 3
        envelope = math.exp(-6 * t)
        sample = int(value * envelope * 32767 * 0.6)
        data.extend(struct.pack('<h', sample))
    return data


# --- NEW: HEAVY STEAM BEAM ---
def generate_heavy_steam(duration=1.0):  # Increased to 1.0 second
    """Generates a low-pitched, heavy steam release."""
    data = bytearray()
    samples = int(44100 * duration)

    last_noise = 0

    for i in range(samples):
        t = i / 44100

        # 1. Low Rumble Layer (60Hz constant hum)
        # Gives the sound "weight"
        rumble = math.sin(2 * math.pi * 60 * t) * 0.3

        # 2. Filtered Noise Layer (The "Steam")
        # Raw random(-1, 1) is high pitched.
        # By averaging it with the previous value, we smooth out sharp spikes.
        # This acts as a Low Pass Filter, creating a "Deep" rushing sound.
        raw_noise = random.uniform(-1, 1)
        noise = (last_noise + raw_noise) / 2.0
        last_noise = noise

        # 3. Combine
        signal = noise + rumble

        # 4. Envelope (Fade In and Out)
        # Fade in quickly (0.1s) to avoid popping
        if t < 0.1:
            env = t / 0.1
        # Fade out slowly at the end
        elif t > (duration - 0.2):
            env = (duration - t) / 0.2
        else:
            env = 1.0

        # 5. Volume Scaling (0.4 to prevent ear-blasting)
        sample = int(signal * env * 32767 * 0.4)

        # Clip to 16-bit range just in case
        sample = max(-32767, min(32767, sample))

        data.extend(struct.pack('<h', sample))
    return data


def generate_musical_ambience(duration=60.0):
    """
    Generates a Sequenced Dark Ambient Track.
    - Chimes: Deep Octave (E4-E5) for a heavy iron bell sound.
    - Mix: Melodic pads are dominant, wind noise is subtle.
    """
    data = bytearray()
    samples_count = int(44100 * duration)

    # --- MUSICAL STRUCTURE (Pads) ---
    chord_1 = [82.41, 123.47, 164.81]  # E minor
    chord_2 = [65.41, 98.00, 130.81]  # C Major
    chord_3 = [55.00, 110.00, 164.81]  # A Minor
    chord_4 = [87.31, 130.81, 174.61]  # F Major
    progression = [chord_1, chord_2, chord_3, chord_4]
    chord_duration = duration / 4.0

    # --- WIND CHIME SETUP (E Harmonic Minor - DEEP Octave) ---
    # Dropped another octave. Range: E4 to E5.
    chime_notes = [
        329.63,  # E4 (Root)
        392.00,  # G4 (Min 3rd)
        493.88,  # B4 (5th)
        523.25,  # C5 (Min 6th - The "Ghostly" note)
        622.25,  # D#5 (Maj 7th - Tension)
        659.25  # E5 (High Root)
    ]

    chime_voices = [{'timer': 0, 'freq': 0, 'duration': 0} for _ in range(3)]

    print(f"Synthesizing {duration}s Atmosphere (Melodic Mix)...")

    # State Variables
    brown_val = 0.0

    for i in range(samples_count):
        t = i / 44100

        # 1. CHORD SEQUENCER
        current_chord_idx = int(t / chord_duration) % 4
        next_chord_idx = (current_chord_idx + 1) % 4
        local_t = (t % chord_duration) / chord_duration

        vol_current = 1.0
        if local_t > 0.8: vol_current = (1.0 - local_t) / 0.2
        vol_next = 0.0
        if local_t > 0.8: vol_next = (local_t - 0.8) / 0.2

        def get_chord_sample(chord, time_val):
            val = 0
            for idx, freq in enumerate(chord):
                osc = math.sin(2 * math.pi * freq * time_val)
                lfo = math.sin(time_val * (0.5 + idx * 0.1)) * 0.2 + 0.8
                val += osc * 0.5 * lfo

            # --- VOLUME BOOST ---
            # Increased from 0.12 to 0.25 to make chords the main focus
            return val * 0.25

        pad_signal = (get_chord_sample(progression[current_chord_idx], t) * vol_current)
        if vol_next > 0:
            pad_signal += (get_chord_sample(progression[next_chord_idx], t) * vol_next)

        # 2. WIND GUSTS (Background)
        delta = random.uniform(-0.05, 0.05)
        brown_val = (brown_val + delta) * 0.99

        # --- VOLUME CUT ---
        # Reduced from 0.08 to 0.04 (Subtle background texture only)
        air_layer = brown_val * 0.04

        gust_strength = (math.sin(t * 0.35) + math.sin(t * 0.2)) * 0.5 + 0.5

        # 3. CHIME LOGIC
        if random.random() < (0.0001 * gust_strength ** 4):
            for voice in chime_voices:
                if voice['timer'] <= 0:
                    voice['freq'] = random.choice(chime_notes)
                    voice['freq'] *= random.uniform(0.998, 1.002)
                    # Deep bells ring longer: 4s to 8s
                    voice['duration'] = random.randint(176400, 352800)
                    voice['timer'] = voice['duration']
                    break

        # Render Voices
        chime_layer = 0
        for voice in chime_voices:
            if voice['timer'] > 0:
                vt = 1.0 - (voice['timer'] / voice['duration'])
                time_elapsed = vt * (voice['duration'] / 44100)

                wave_samp = math.sin(2 * math.pi * voice['freq'] * time_elapsed)
                # Slower decay for heavy bells
                decay = math.exp(-0.5 * time_elapsed)

                chime_layer += wave_samp * decay * (1.0 - vt) * 0.15
                voice['timer'] -= 1

        # 4. MASTER MIX
        signal = pad_signal + air_layer + chime_layer

        if t < 1.0:
            signal *= t
        elif t > (duration - 1.0):
            signal *= (duration - t)

        signal = max(-1.0, min(1.0, signal))
        sample = int(signal * 32767 * 0.7)
        data.extend(struct.pack('<h', sample))

    return data


def generate_dark_eyes_melody():
    """
    Generates 'The Eyes of Texas' in its ORIGINAL D Major (Sheet Music Accurate).
    Use this to verify the rhythm and melody.
    """
    print("Synthesizing Verification: The Eyes of Texas (D Major)...")

    # 1. Define Frequencies (D Major)
    # A4, B4, C#5, D5, E5, F#5, G5
    N_G4 = 392.00
    N_A4 = 440.00  # Pickup / End
    N_B4 = 493.88
    N_D5 = 587.33  # Root
    N_E5 = 659.25
    N_Fsharp5 = 739.99

    # 2. Define Rhythm (6/8 Time)
    # 1 Tick = Eighth Note
    tick = 0.22  # Slightly faster for the waltz feel

    # (Frequency, Duration in Ticks)
    melody = [
        # Pickup
        (N_A4, 1),  # "The" (Eighth)

        # Bar 1
        (N_D5, 2),  # "Eyes" (Quarter)
        (N_E5, 1),  # "of"   (Eighth)
        (N_Fsharp5, 2),  # "Tex-" (Quarter)
        (N_D5, 1),  # "-as"  (Eighth)

        # Bar 2
        (N_B4, 2),  # "are"  (Quarter)
        (N_A4, 1),  # "up-"  (Eighth)
        (N_G4, 3),  # "-on"  (Dotted Quarter)

        # Bar 3
        (N_A4, 6),  # "you"  (Dotted Half)
    ]

    # Calculate length
    total_ticks = sum(note[1] for note in melody)
    total_seconds = (total_ticks * tick) + 4.0
    total_samples = int(44100 * total_seconds)

    master_buffer = [0.0] * total_samples

    current_sample_idx = 0

    for freq, duration_ticks in melody:
        # Standard clear bell sound for verification
        note_samples = int(44100 * 3.0)

        for i in range(note_samples):
            if current_sample_idx + i >= total_samples: break

            t = i / 44100

            # Bright Brass/Bell Tone
            wave = math.sin(2 * math.pi * freq * t)
            wave += 0.5 * math.sin(2 * math.pi * freq * 2 * t)

            env = math.exp(-1.5 * t)

            val = wave * env * 0.4
            master_buffer[current_sample_idx + i] += val

        current_sample_idx += int(duration_ticks * tick * 44100)

    # Write
    data = bytearray()
    for samp in master_buffer:
        samp = max(-1.0, min(1.0, samp))
        int_val = int(samp * 32767)
        data.extend(struct.pack('<h', int_val))

    return data


if __name__ == "__main__":
    # ... (Previous generations) ...
    write_wav("steam_shoot.wav", generate_steam_hiss(0.15))
    write_wav("aoe_thud.wav", generate_thud(0.4))
    write_wav("build_clang.wav", generate_clang(0.3))
    write_wav("laser_hum.wav", generate_heavy_steam(1.0))
    write_wav("ambience_loop.wav", generate_musical_ambience(60.0))

    # --- Generate the Easter Egg ---
    write_wav("easter_egg.wav", generate_dark_eyes_melody())

    print("Done! Assets updated.")