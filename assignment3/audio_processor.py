import subprocess
import os
import numpy as np
from typing import List, Tuple
import tempfile
import shutil

def check_sox_installation():
    """
    Check if SoX is properly installed and available in the system path.
    Raises RuntimeError if SoX is not found.
    """
    if not shutil.which('sox'):
        raise RuntimeError(
            "SoX is not installed or not in system PATH. "
            "Please install SoX:\n"
            "  Ubuntu/Debian: sudo apt-get install sox\n"
            "  macOS: brew install sox\n"
            "  Windows: Download from https://sourceforge.net/projects/sox/"
        )

def convert_to_wav(input_path: str, output_path: str, sample_rate: int = 44100):
    """
    Convert audio file to WAV format using SoX.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save WAV file
        sample_rate: Target sample rate (default: 44100 Hz)
    """
    check_sox_installation()
    cmd = ['sox', input_path, '-r', str(sample_rate), output_path]
    subprocess.run(cmd, check=True)

def extract_segment(input_path: str, output_path: str, start_time: float, duration: float):
    """
    Extract a segment from an audio file using SoX.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save segment
        start_time: Start time in seconds
        duration: Duration in seconds
    """
    check_sox_installation()
    cmd = ['sox', input_path, output_path, 'trim', str(start_time), str(duration)]
    subprocess.run(cmd, check=True)

def add_noise(input_path: str, output_path: str, snr_db: float = 20):
    """
    Add white noise to an audio file with specified SNR using SoX.
    
    Args:
        input_path: Path to input audio file
        output_path: Path to save noisy audio
        snr_db: Signal-to-noise ratio in dB
    """
    check_sox_installation()
    # Generate noise file
    noise_path = 'temp_noise.wav'
    cmd = ['sox', '-n', noise_path, 'synth', '10', 'whitenoise', 'vol', '0.5']
    subprocess.run(cmd, check=True)
    
    # Mix with original audio
    cmd = ['sox', '-m', input_path, noise_path, output_path, 'vol', str(snr_db)]
    subprocess.run(cmd, check=True)
    
    # Clean up
    os.remove(noise_path)

def get_max_frequencies(audio_path: str, n_freqs: int = 4) -> List[float]:
    """
    Extract the most significant frequencies from an audio file using GetMaxFreqs.
    
    Args:
        audio_path: Path to audio file
        n_freqs: Number of frequencies to extract (default: 4)
        
    Returns:
        List of most significant frequencies
    """
    # Convert to WAV if needed
    if not audio_path.endswith('.wav'):
        with tempfile.NamedTemporaryFile(suffix='.wav') as temp_wav:
            convert_to_wav(audio_path, temp_wav.name)
            audio_path = temp_wav.name
    
    # Create temporary file for frequencies
    with tempfile.NamedTemporaryFile(suffix='.freqs') as temp_freqs:
        # Run GetMaxFreqs
        cmd = ['GetMaxFreqs/bin/GetMaxFreqs', '-w', temp_freqs.name, '-nf', str(n_freqs), audio_path]
        subprocess.run(cmd, check=True)
        
        # Read frequencies from binary file
        with open(temp_freqs.name, 'rb') as f:
            freqs_bytes = f.read()
        
        # Convert bytes to frequencies
        # Each frequency is stored as a byte (0-255)
        # Convert to actual frequency: freq = index * (sample_rate / window_size)
        freqs = []
        for b in freqs_bytes:
            freq = b * (44100 / 1024)  # 44100 Hz sample rate, 1024 window size
            freqs.append(freq)
    
    return freqs

def prepare_database(input_dir: str, output_dir: str):
    """
    Prepare a database of audio files by converting to WAV and extracting signatures.
    
    Args:
        input_dir: Directory containing input audio files
        output_dir: Directory to save processed files and signatures
    """
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(('.mp3', '.wav', '.ogg', '.flac')):
            input_path = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            
            # Convert to WAV if needed
            if not filename.endswith('.wav'):
                wav_path = os.path.join(output_dir, f"{base_name}.wav")
                convert_to_wav(input_path, wav_path)
            else:
                wav_path = input_path
            
            # Extract frequencies
            freqs = get_max_frequencies(wav_path)
            
            # Save frequencies
            freq_path = os.path.join(output_dir, f"{base_name}.freq")
            np.save(freq_path, freqs) 