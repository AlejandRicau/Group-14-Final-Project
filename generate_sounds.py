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


def generate_musical_ambience(duration=120.0):
    """
    Generates a Seamlessly Looping Dark Ambient Track.
    - Duration: 120 seconds (2 minutes) for variety.
    - Seamless: Reverb tails wrap around from end to start.
    - Music: Extended 8-bar progression.
    """
    # We generate slightly MORE audio than needed to handle the wrap-around tail
    tail_duration = 5.0
    total_duration = duration + tail_duration
    samples_count = int(44100 * total_duration)
    loop_point = int(44100 * duration)

    data = bytearray()

    # --- MUSICAL STRUCTURE (Extended) ---
    # 8-Chord Progression to reduce repetition:
    # Em -> C -> Am -> F -> Em -> G -> Bm -> D#dim
    c_Em = [82.41, 123.47, 164.81]
    c_C = [65.41, 98.00, 130.81]
    c_Am = [55.00, 110.00, 164.81]
    c_F = [87.31, 130.81, 174.61]
    c_G = [98.00, 146.83, 196.00]  # G Major (Hope)
    c_Bm = [61.74, 123.47, 185.00]  # B Minor (Dark)
    c_DS = [77.78, 123.47, 155.56]  # D# Diminished (Tension)

    progression = [c_Em, c_C, c_Am, c_F, c_Em, c_G, c_Bm, c_DS]
    chord_duration = duration / 8.0  # 15s per chord

    # --- CHIME NOTES (E Harmonic Minor - Deep) ---
    chime_notes = [329.63, 392.00, 493.88, 523.25, 622.25, 659.25]
    chime_voices = [{'timer': 0, 'freq': 0, 'duration': 0} for _ in range(3)]

    print(f"Synthesizing {duration}s Seamless Atmosphere...")

    # Intermediate buffer (Float) to handle mixing before int conversion
    mix_buffer = [0.0] * samples_count

    # State
    brown_val = 0.0

    for i in range(samples_count):
        t = i / 44100

        # 1. SEQUENCER
        # We wrap the index using modulo so the tail plays the start of the loop
        loop_t = t % duration

        current_chord_idx = int(loop_t / chord_duration) % 8
        next_chord_idx = (current_chord_idx + 1) % 8
        local_t = (loop_t % chord_duration) / chord_duration

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
            return val * 0.25

        pad_signal = (get_chord_sample(progression[current_chord_idx], t) * vol_current)
        if vol_next > 0:
            pad_signal += (get_chord_sample(progression[next_chord_idx], t) * vol_next)

        # 2. WIND (Continuous)
        delta = random.uniform(-0.05, 0.05)
        brown_val = (brown_val + delta) * 0.99
        air_layer = brown_val * 0.04
        gust_strength = (math.sin(t * 0.35) + math.sin(t * 0.2)) * 0.5 + 0.5

        # 3. CHIMES
        if random.random() < (0.0001 * gust_strength ** 4):
            for voice in chime_voices:
                if voice['timer'] <= 0:
                    voice['freq'] = random.choice(chime_notes)
                    voice['freq'] *= random.uniform(0.998, 1.002)
                    voice['duration'] = random.randint(176400, 352800)
                    voice['timer'] = voice['duration']
                    break

        chime_layer = 0
        for voice in chime_voices:
            if voice['timer'] > 0:
                vt = 1.0 - (voice['timer'] / voice['duration'])
                time_elapsed = vt * (voice['duration'] / 44100)
                wave_samp = math.sin(2 * math.pi * voice['freq'] * time_elapsed)
                decay = math.exp(-0.5 * time_elapsed)
                chime_layer += wave_samp * decay * (1.0 - vt) * 0.15
                voice['timer'] -= 1

        # Store float sample
        mix_buffer[i] = pad_signal + air_layer + chime_layer

    # --- WRAP AROUND MIXING ---
    # Take the 'Tail' (audio past the loop point) and add it to the 'Head' (start)
    # This makes the reverb/release of the last chord blend into the first chord.

    final_buffer = mix_buffer[:loop_point]  # Truncate to exact duration

    for i in range(int(44100 * tail_duration)):
        if loop_point + i < len(mix_buffer):
            # Add the tail to the start
            if i < len(final_buffer):
                final_buffer[i] += mix_buffer[loop_point + i]

    # Write Final WAV
    for samp in final_buffer:
        samp = max(-1.0, min(1.0, samp))
        int_val = int(samp * 32767 * 0.7)
        data.extend(struct.pack('<h', int_val))

    return data


def generate_dark_eyes_melody():
    """
    Generates 'The Eyes of Texas' using your corrected rhythm.
    Transposed to G Minor (B -> Bb) for the dark vibe.
    """
    print("Synthesizing Easter Egg: The Eyes of Texas (Corrected Dark)...")

    # 1. Define Frequencies (G Minor)
    N_D4 = 293.66  # Low 5th
    N_G4 = 392.00  # Root
    N_A4 = 440.00  # 2nd
    N_Bb4 = 466.16  # Minor 3rd (The "Sad" Note - replaces B4)

    # 2. Define Rhythm
    # Beat = 0.35 seconds (Slow but recognizable)
    beat = 0.35

    # (Frequency, Duration in Beats)
    # Using your exact rhythm, but swapping B4 for Bb4
    melody = [
        # "The" (Pickup)
        (N_D4, 1.5),

        # "Eyes of Tex-as"
        (N_G4, 2.5),  # Eyes
        (N_D4, 0.5),  # of
        (N_G4, 1.0),  # Tex
        (N_D4, 0.5),  # as

        # "are up-on"
        (N_G4, 1.0),  # are
        (N_A4, 0.5),  # up
        (N_Bb4, 3.0),  # on (The Dark Note!)

        # "you"
        (N_G4, 3.0),  # you
    ]

    # Calculate length
    total_beats = sum(note[1] for note in melody)
    total_seconds = (total_beats * beat) + 5.0
    total_samples = int(44100 * total_seconds)

    master_buffer = [0.0] * total_samples

    current_sample_idx = 0

    for freq, duration_beats in melody:
        # Long ring time for atmosphere
        note_samples = int(44100 * 4.0)

        for i in range(note_samples):
            if current_sample_idx + i >= total_samples: break

            t = i / 44100

            # Heavy Iron Bell Tone
            wave = math.sin(2 * math.pi * freq * t)
            # Add the Minor 3rd harmonic explicitly to reinforce the darkness
            wave += 0.5 * math.sin(2 * math.pi * (freq * 1.2) * t)
            # Sub-octave for weight
            wave += 0.3 * math.sin(2 * math.pi * (freq * 0.5) * t)

            # Envelope
            env = math.exp(-1.0 * t)

            val = wave * env * 0.4
            master_buffer[current_sample_idx + i] += val

        current_sample_idx += int(duration_beats * beat * 44100)

    # Write
    data = bytearray()
    for samp in master_buffer:
        samp = max(-1.0, min(1.0, samp))
        int_val = int(samp * 32767)
        data.extend(struct.pack('<h', int_val))

    return data


def generate_servo_slide(duration=0.4):
    """
    Generates a mechanical 'sliding' sound for the menu opening.
    Technique: Sine wave rising in pitch + chopped noise for texture.
    """
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100

        # Rising Pitch (Motor whine)
        freq = 100 + (t * 400)
        motor = math.sin(2 * math.pi * freq * t) * 0.3

        # Texture (The "sliding" friction)
        friction = random.uniform(-0.5, 0.5)

        # Envelope: Fade in/out
        env = math.sin(t / duration * 3.14)

        signal = (motor + friction) * env * 0.5
        data.extend(struct.pack('<h', int(signal * 32767)))
    return data


def generate_switch_click(duration=0.05):
    """
    Generates a sharp, high-pitched mechanical click for selection.
    """
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100

        # Very fast high frequency chirp
        wave = math.sin(2 * math.pi * 2000 * t)

        # Instant decay
        env = math.exp(-80 * t)

        signal = wave * env * 0.6
        data.extend(struct.pack('<h', int(signal * 32767)))
    return data


def generate_error_buzz(duration=0.3):
    """
    Generates a 'Stuck Valve' sound (Low Dissonant Buzz).
    Technique: Sawtooth wave + Sine wave interference.
    """
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100

        # Base Low Tone (80Hz)
        base = math.sin(2 * math.pi * 80 * t)

        # Interference (85Hz) to create a "wobble" or "stuck" feel
        wobble = math.sin(2 * math.pi * 85 * t)

        # Buzz (Square/Sawish approximation)
        buzz = 1.0 if (t * 80) % 1.0 > 0.5 else -1.0

        # Mix: Mostly base, some buzz
        signal = (base * 0.5) + (wobble * 0.3) + (buzz * 0.1)

        # Short envelope
        env = math.exp(-10 * t)

        signal *= env * 0.5
        data.extend(struct.pack('<h', int(signal * 32767)))
    return data


def generate_servo_slide_down(duration=0.4):
    """
    Generates a mechanical 'sliding' sound with DECREASING pitch (Menu Close).
    """
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100

        # Falling Pitch: Starts high (500), drops to low (100)
        # Original was: 100 + (t * 400)
        freq = 500 - (t * 400)

        motor = math.sin(2 * math.pi * freq * t) * 0.3
        friction = random.uniform(-0.5, 0.5)
        env = math.sin(t / duration * 3.14)

        signal = (motor + friction) * env * 0.5
        data.extend(struct.pack('<h', int(signal * 32767)))
    return data


def generate_ui_pause(duration=0.25):
    """'Power Down' effect: Sine wave dropping pitch rapidly."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        # Pitch drop: 600Hz -> 50Hz
        freq = 600 * math.exp(-10 * t)
        val = math.sin(2 * math.pi * freq * t)
        # Fade out
        env = 1.0 - (i / samples)
        sample = int(val * env * 32767 * 0.5)
        data.extend(struct.pack('<h', sample))
    return data


def generate_ui_unpause(duration=0.25):
    """'Power Up' effect: Sine wave rising pitch rapidly."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        # Pitch rise: 100Hz -> 600Hz
        freq = 100 + (500 * (i / samples) ** 2)
        val = math.sin(2 * math.pi * freq * t)
        # Fade in/out
        env = math.sin(t / duration * 3.14)
        sample = int(val * env * 32767 * 0.5)
        data.extend(struct.pack('<h', sample))
    return data


def generate_ui_speed_up(duration=0.2):
    """High pitched 'Warp' sound."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        # Slide 400Hz -> 1200Hz
        freq = 400 + (800 * (i / samples))
        # Square-ish wave for "digital" feel
        val = 0.5 * math.sin(2 * math.pi * freq * t)
        val += 0.25 * math.sin(2 * math.pi * (freq * 2) * t)

        env = 1.0 - (i / samples)
        sample = int(val * env * 32767 * 0.4)
        data.extend(struct.pack('<h', sample))
    return data


def generate_ui_slow_down(duration=0.2):
    """Lower pitched 'Brake' sound."""
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100
        # Slide 1200Hz -> 400Hz
        freq = 1200 - (800 * (i / samples))

        val = 0.5 * math.sin(2 * math.pi * freq * t)
        val += 0.25 * math.sin(2 * math.pi * (freq * 2) * t)

        env = 1.0 - (i / samples)
        sample = int(val * env * 32767 * 0.4)
        data.extend(struct.pack('<h', sample))
    return data


def generate_player_hurt(duration=0.4):
    """
    Generates a heavy 'Hull Breach' impact sound.
    Low frequency thud + white noise burst.
    """
    data = bytearray()
    samples = int(44100 * duration)
    for i in range(samples):
        t = i / 44100

        # 1. Impact (Low Sine drop)
        freq = 100 * math.exp(-15 * t)
        impact = math.sin(2 * math.pi * freq * t)

        # 2. Crunch (Noise)
        noise = random.uniform(-1, 1) * math.exp(-10 * t)

        # 3. Alarm undertone (Square wave)
        alarm = 0.0
        if t > 0.1:  # Delayed alarm
            alarm = 0.3 if math.sin(2 * math.pi * 400 * t) > 0 else -0.3
            alarm *= math.exp(-5 * (t - 0.1))

        signal = (impact * 0.6) + (noise * 0.3) + (alarm * 0.2)
        data.extend(struct.pack('<h', int(signal * 32767)))
    return data


def generate_snare_cadence(duration=8.0):
    """
    Generates a military snare drum march.
    Rhythm: 1, 2-and, 3, 4-and-a (Marching Cadence)
    """
    data = bytearray()
    samples_count = int(44100 * duration)
    master_buffer = [0.0] * samples_count

    # Snare Sound Generator (Noise + Tone)
    def add_hit(start_index, velocity):
        length = 4000  # 0.1s
        for i in range(length):
            if start_index + i >= samples_count: break
            t = i / 44100

            # White Noise (The Snares)
            noise = random.uniform(-1, 1)
            # Sine Tone (The Drum Head) - 180Hz
            tone = math.sin(2 * math.pi * 180 * t)

            # Envelope: Instant attack, fast decay
            env = math.exp(-30 * t)

            val = (noise * 0.7 + tone * 0.3) * env * velocity
            master_buffer[start_index + i] += val

    # Sequencer (100 BPM)
    beat_len = 0.6  # Seconds per beat
    samples_per_beat = int(beat_len * 44100)

    cursor = 0
    while cursor < samples_count - samples_per_beat * 4:
        # Beat 1: BOOM
        add_hit(cursor, 1.0)

        # Beat 2: tat-tat
        add_hit(cursor + samples_per_beat, 0.6)
        add_hit(cursor + samples_per_beat + int(samples_per_beat / 2), 0.5)

        # Beat 3: BOOM
        add_hit(cursor + samples_per_beat * 2, 0.9)

        # Beat 4: trrr-pup (Roll)
        s4 = cursor + samples_per_beat * 3
        add_hit(s4, 0.5)
        add_hit(s4 + int(samples_per_beat / 4), 0.4)
        add_hit(s4 + int(samples_per_beat / 2), 0.6)

        cursor += samples_per_beat * 4

    # Write to bytes
    for samp in master_buffer:
        samp = max(-1.0, min(1.0, samp))
        data.extend(struct.pack('<h', int(samp * 32767 * 0.5)))

    return data


def generate_game_start(duration=1.5):
    """
    Generates a 'Hydraulic Airlock' sound for starting the game.
    Layers: Heavy Clunk + Steam Release + Rising Tone.
    """
    data = bytearray()
    samples = int(44100 * duration)

    for i in range(samples):
        t = i / 44100

        # 1. The Lock (Heavy Clunk at start)
        clunk = 0
        if t < 0.2:
            # Low frequency impact
            clunk = math.sin(2 * math.pi * 60 * t) * math.exp(-20 * t)
            # Add noise burst for texture
            clunk += random.uniform(-0.5, 0.5) * math.exp(-30 * t)

        # 2. The Steam (Hissing release)
        # Starts quiet, swells up, then fades
        steam = random.uniform(-0.4, 0.4)
        steam_env = 0
        if t > 0.1:
            # Fade in
            steam_env = math.sin((t - 0.1) * 3.0)
            if steam_env < 0: steam_env = 0  # Clamp to positive part of sine
            steam_env *= math.exp(-2 * (t - 0.1))

        # 3. The Servo (Rising tone)
        freq = 100 + (t * 200)
        servo = math.sin(2 * math.pi * freq * t) * 0.2 * math.exp(-2 * t)

        signal = (clunk * 0.8) + (steam * steam_env * 0.6) + servo

        data.extend(struct.pack('<h', int(signal * 32767 * 0.8)))

    return data

if __name__ == "__main__":
    write_wav("steam_shoot.wav", generate_steam_hiss(0.15))
    write_wav("aoe_thud.wav", generate_thud(0.4))
    write_wav("build_clang.wav", generate_clang(0.3))
    write_wav("laser_hum.wav", generate_heavy_steam(1.0))
    write_wav("ambience_loop.wav", generate_musical_ambience(120.0))
    write_wav("easter_egg.wav", generate_dark_eyes_melody())
    write_wav("ui_menu.wav", generate_servo_slide(0.3))
    write_wav("ui_click.wav", generate_switch_click(0.05))
    write_wav("ui_error.wav", generate_error_buzz(0.3))
    write_wav("ui_menu_close.wav", generate_servo_slide_down(0.3))
    write_wav("ui_pause.wav", generate_ui_pause())
    write_wav("ui_unpause.wav", generate_ui_unpause())
    write_wav("ui_speed_up.wav", generate_ui_speed_up())
    write_wav("ui_slow_down.wav", generate_ui_slow_down())
    write_wav("player_hurt.wav", generate_player_hurt())
    write_wav("ui_march.wav", generate_snare_cadence(8.0))
    write_wav("ui_start.wav", generate_game_start(1.5))

    print("Done! Assets updated.")