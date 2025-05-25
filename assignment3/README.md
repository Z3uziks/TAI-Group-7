# Music Identification using Normalized Compression Distance

This project implements a music identification system using Normalized Compression Distance (NCD) as described in the paper by Rudi Cilibrasi et al. The system can identify music segments by comparing them against a database of known songs using various compression algorithms.

## Requirements

- Python 3.7+
- Required Python packages (install using `pip install -r requirements.txt`):
  - numpy
  - matplotlib
  - tqdm
- System requirements:
  - SoX (Sound eXchange) for audio processing
  - gzip
  - bzip2
  - lzma
  - zstd
  - libsndfile (for GetMaxFreqs)
  - FFTW3 (for GetMaxFreqs)

## Project Structure

```
.
├── music_identifier.py     # Main implementation
├── audio_processor.py      # Audio processing utilities
├── test_music_identifier.py # Testing and evaluation
├── requirements.txt        # Python dependencies
├── GetMaxFreqs/           # Frequency extraction program
│   ├── src/               # Source code
│   └── bin/               # Compiled binaries
├── music_database/        # Directory for full music files
├── query_segments/        # Directory for query segments
└── results/              # Directory for results and plots
```

## Setup

1. Install system dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install sox libsndfile1-dev libfftw3-dev
   
   # macOS
   brew install sox libsndfile fftw
   
   # Windows
   # Download SoX from https://sourceforge.net/projects/sox/
   # Download libsndfile and FFTW3 from their respective websites
   ```

2. Compile GetMaxFreqs:
   ```bash
   cd GetMaxFreqs/src
   make -f Makefile.linux  # or Makefile.windows for Windows
   cd ../..
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create the necessary directories:
   ```bash
   mkdir -p music_database query_segments results
   ```

5. Place your full music files in the `music_database` directory.

## Usage

### Basic Usage

```python
from music_identifier import MusicIdentifier

# Initialize with a specific compressor
identifier = MusicIdentifier(compressor='gzip')  # Options: 'gzip', 'bzip2', 'lzma', 'zstd'

# Add music to database
identifier.add_to_database('music_database/song1.wav', 'song1')

# Identify a query segment
predicted_name, ncd_value = identifier.identify('query_segments/segment1.wav')
print(f"Predicted: {predicted_name}, NCD: {ncd_value}")
```

### Running Tests

To evaluate the system with different compressors:

```bash
python test_music_identifier.py
```

This will:
1. Extract 10-second segments from the middle of each music file
2. Test each compressor on clean query segments
3. Test each compressor on noisy query segments
4. Generate comparison plots in the `results` directory

## How It Works

1. **Signature Extraction**: Each audio file is converted into a signature by:
   - Using SoX to process the audio (conversion, segmentation, noise addition)
   - Using GetMaxFreqs to extract significant frequencies:
     - Processes audio in overlapping windows (1024 samples with 256 sample overlap)
     - Converts stereo to mono and downsamples by a factor of 4
     - Computes FFT on each window
     - Extracts the 4 most significant frequencies from each window
   - Converting these frequencies into a string representation

2. **NCD Computation**: The Normalized Compression Distance is computed using:
   ```
   NCD(x, y) = (C(xy) - min(C(x), C(y))) / max(C(x), C(y))
   ```
   where C(x) is the compressed size of x.

3. **Identification**: A query segment is identified by finding the music in the database that yields the smallest NCD value.

## Notes

- The system works best with WAV files, but MP3 files are also supported.
- For best results, ensure your query segments are at least 10 seconds long.
- The system is robust to noise, as demonstrated in the test script.
- Different compressors may yield different results; the test script helps identify the best performer for your specific use case.
- The implementation uses the GetMaxFreqs program for frequency extraction, which is based on the approach described in the paper.
- SoX is used as a command-line tool for audio processing. The included `sox-14.4.2` directory contains the source code for reference, but the system uses the installed SoX binary from your system. 