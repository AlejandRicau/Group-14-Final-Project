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
    Progression: Em -> C -> Am -> F (i - VI - iv - II)
    Features: Consistent Chord Changes, Frequent Metallic FX, Seamless Loop.
    """
    data = bytearray()
    samples_count = int(44100 * duration)

    # --- MUSICAL STRUCTURE ---
    # Chords (frequencies in Hz)
    # E Minor (Root)
    chord_1 = [82.41, 123.47, 164.81]  # E2, B2, E3
    # C Major (The looming giant)
    chord_2 = [65.41, 98.00, 130.81]  # C2, G2, C3
    # A Minor (The sadness)
    chord_3 = [55.00, 110.00, 164.81]  # A1, A2, E3
    # F Major (The Phrygian Tension)
    chord_4 = [87.31, 130.81, 174.61]  # F2, C3, F3

    progression = [chord_1, chord_2, chord_3, chord_4]

    # Timing
    chord_duration = duration / 4.0  # 15 seconds per chord

    # --- METALLIC FX SCHEDULER ---
    # We want them frequent. Let's schedule one every ~2-4 seconds.
    chime_events = []
    cursor = 2.0
    while cursor < duration - 2.0:  # Don't start chimes at very end
        chime_events.append(int(cursor * 44100))
        cursor += random.uniform(2.0, 4.0)  # Gap between chimes

    # State Variables
    brown_val = 0.0

    print(f"Synthesizing {duration}s Sequenced Atmosphere...")

    for i in range(samples_count):
        t = i / 44100

        # 1. SEQUENCER LOGIC
        # Determine which chord is active based on time
        current_chord_idx = int(t / chord_duration) % 4
        next_chord_idx = (current_chord_idx + 1) % 4

        # Calculate progress within the current chord's window (0.0 to 1.0)
        local_t = (t % chord_duration) / chord_duration

        # Crossfade Logic:
        # Fade OUT current chord in last 20% of its time
        # Fade IN next chord in first 20% of its time

        vol_current = 1.0
        if local_t > 0.8:  # Fading out
            vol_current = (1.0 - local_t) / 0.2

        vol_next = 0.0
        if local_t > 0.8:  # Pre-fading in the next one for overlap
            vol_next = (local_t - 0.8) / 0.2

        # 2. GENERATE PADS
        # Function to generate a chord sample
        def get_chord_sample(chord, time_val):
            val = 0
            for idx, freq in enumerate(chord):
                # Add slight detune for "thick" analog sound
                osc1 = math.sin(2 * math.pi * freq * time_val)
                osc2 = math.sin(2 * math.pi * (freq * 1.01) * time_val)
                # Slow breathing LFO specific to this note
                lfo = math.sin(time_val * (0.5 + idx * 0.1)) * 0.2 + 0.8
                val += (osc1 + osc2) * 0.5 * lfo
            return val * 0.15  # Low master volume for pads

        pad_signal = (get_chord_sample(progression[current_chord_idx], t) * vol_current)

        # If we are in the transition zone, add the next chord too
        if vol_next > 0:
            pad_signal += (get_chord_sample(progression[next_chord_idx], t) * vol_next)

        # 3. METALLIC CHIMES (Frequent)
        chime_layer = 0
        for start_sample in chime_events:
            offset = i - start_sample
            if 0 <= offset < 44100:  # 1 second duration
                ct = offset / 44100
                # FM Synthesis for "Clang" sound
                # Carrier: 880Hz, Modulator: 220Hz
                mod_idx = 5.0 * math.exp(-10 * ct)  # Modulation fades quickly
                modulator = math.sin(2 * math.pi * 220 * ct) * mod_idx * 220
                carrier = math.sin(2 * math.pi * (880 + modulator) * ct)

                env = math.exp(-5 * ct)
                chime_layer += carrier * env * 0.15

        # 4. ATMOSPHERE (Drone)
        delta = random.uniform(-0.05, 0.05)
        brown_val = (brown_val + delta) * 0.99
        air_layer = brown_val * 0.1

        # 5. MASTER MIX
        signal = pad_mix = pad_signal + chime_layer + air_layer

        # Global Loop Fade (Seamless)
        # Fade the very first and last 0.5s to prevent clicking at loop point
        if t < 0.5:
            signal *= (t / 0.5)
        elif t > (duration - 0.5):
            signal *= ((duration - t) / 0.5)

        signal = max(-1.0, min(1.0, signal))
        sample = int(signal * 32767 * 0.8)
        data.extend(struct.pack('<h', sample))

    return data


if __name__ == "__main__":
    # ... regenerate SFX ...
    write_wav("steam_shoot.wav", generate_steam_hiss(0.15))
    write_wav("aoe_thud.wav", generate_thud(0.4))
    write_wav("build_clang.wav", generate_clang(0.3))
    write_wav("laser_hum.wav", generate_heavy_steam(1.0))

    # Generate New Ambience
    write_wav("ambience_loop.wav", generate_musical_ambience(60.0))