"""Generate simple sound effects for the game."""
import wave
import struct
import math
import os

def generate_sound(filename, duration, sample_rate=44100, channels=1):
    """Base function to generate a WAV file."""
    pass

def generate_shotgun_sound():
    """Generate a shotgun blast sound effect."""
    filename = "assets/sounds/shotgun.wav"
    sample_rate = 44100
    duration = 0.3

    samples = []
    num_samples = int(sample_rate * duration)

    for i in range(num_samples):
        t = i / sample_rate
        # Combine noise burst with low frequency thump
        noise = (hash(i) % 1000 - 500) / 500.0  # Pseudo-random noise
        decay = math.exp(-t * 15)  # Fast decay
        thump = math.sin(2 * math.pi * 80 * t) * math.exp(-t * 10)

        sample = (noise * 0.7 + thump * 0.5) * decay
        sample = max(-1, min(1, sample))  # Clamp
        samples.append(int(sample * 32767))

    # Write WAV file
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Generated {filename}")

def generate_death_sound():
    """Generate enemy death sound effect."""
    filename = "assets/sounds/enemy_death.wav"
    sample_rate = 44100
    duration = 0.5

    samples = []
    num_samples = int(sample_rate * duration)

    for i in range(num_samples):
        t = i / sample_rate
        # Descending tone with some grit
        freq = 400 - (t * 600)  # Descending frequency
        freq = max(freq, 50)

        tone = math.sin(2 * math.pi * freq * t)
        # Add some harmonics for grit
        tone += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
        tone += 0.1 * math.sin(2 * math.pi * freq * 3 * t)

        decay = math.exp(-t * 4)
        sample = tone * decay * 0.5
        sample = max(-1, min(1, sample))
        samples.append(int(sample * 32767))

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Generated {filename}")

def generate_hit_sound():
    """Generate hit marker sound effect."""
    filename = "assets/sounds/hit.wav"
    sample_rate = 44100
    duration = 0.1

    samples = []
    num_samples = int(sample_rate * duration)

    for i in range(num_samples):
        t = i / sample_rate
        # Quick high-pitched tick
        freq = 1200
        tone = math.sin(2 * math.pi * freq * t)
        decay = math.exp(-t * 40)
        sample = tone * decay * 0.4
        sample = max(-1, min(1, sample))
        samples.append(int(sample * 32767))

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Generated {filename}")

if __name__ == "__main__":
    os.makedirs("assets/sounds", exist_ok=True)
    generate_shotgun_sound()
    generate_death_sound()
    generate_hit_sound()
    print("All sounds generated!")
