# Music Identification System using NCD

This project implements a music identification system based on Normalized Compression Distance (NCD) and frequency signatures. It provides tools for building a music database, generating query segments, running identification experiments, and evaluating results.

## Features

- **Signature Extraction:** Uses a custom `GetMaxFreqs` tool to extract frequency signatures from audio files.
- **Noise Robustness:** Supports adding noise to queries for robustness testing.
- **Multiple Compressors:** Supports `gzip`, `bzip2`, `lzma`, and `zstd` for NCD calculation.
- **Batch Experiments:** Run large-scale identification experiments and save results.
- **Evaluation & Visualization:** Tools for accuracy evaluation and performance plotting.

## Directory Structure

```
assignment3/
├── database/         # Place your music files here (wav, flac, mp3)
├── signatures/       # Generated frequency signatures
├── queries/          # Generated query segments
├── results/          # Experiment results and plots
├── src/              # Source code (core modules)
├── scripts/          # Utility scripts (setup, generate, run, etc.)
├── GetMaxFreqs/      # Frequency extraction tool (binary required)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

You also need:
- **sox** (for audio processing):  
  ```bash
  sudo apt-get install sox libsox-fmt-all
  ```
- **GetMaxFreqs** binary:  
  Place the compiled `GetMaxFreqs` executable in `GetMaxFreqs/bin/`.

### 2. Prepare the Database

Place at least 25 music files (`.wav`, `.flac`, `.mp3`) in the `database/` directory.

#### Default Database Contents

##### Music Database Files

| Music File (.wav) | Signature File (.freqs) | Artist | Song Name |
|------------------|-------------------------|---------|------------|
| BigXthaPlug - All The Way feat. Bailey Zimmerman.wav | BigXthaPlug - All The Way feat. Bailey Zimmerman.freqs | BigXthaPlug ft. Bailey Zimmerman | All The Way |
| BigXthaPlug - Change Me.wav | BigXthaPlug - Change Me.freqs | BigXthaPlug | Change Me |
| Carlos Paredes - Canção Verdes Anos.wav | Carlos Paredes - Canção Verdes Anos.freqs | Carlos Paredes | Canção Verdes Anos |
| DRAKE - FAMILY MATTERS.wav | DRAKE - FAMILY MATTERS.freqs | Drake | Family Matters |
| DRAKE - NOKIA.wav | DRAKE - NOKIA.freqs | Drake | Nokia |
| Eminem - Houdini.wav | Eminem - Houdini.freqs | Eminem | Houdini |
| Eminem - Tobey feat. Big Sean & BabyTron.wav | Eminem - Tobey feat. Big Sean & BabyTron.freqs | Eminem ft. Big Sean & BabyTron | Tobey |
| Hanumankind, Kalmi - Hanumankind Big Dawgs.wav | Hanumankind, Kalmi - Hanumankind Big Dawgs.freqs | Hanumankind, Kalmi | Big Dawgs |
| Kendrick Lamar - Euphoria.wav | Kendrick Lamar - Euphoria.freqs | Kendrick Lamar | Euphoria |
| Lil Tecca - Dark Thoughts.wav | Lil Tecca - Dark Thoughts.freqs | Lil Tecca | Dark Thoughts |
| Lil Tecca - OWA OWA.wav | Lil Tecca - OWA OWA.freqs | Lil Tecca | OWA OWA |
| Metallica - The Memory Remains.wav | Metallica - The Memory Remains.freqs | Metallica | The Memory Remains |
| Mozart Requiem Sanctus.wav | Mozart Requiem Sanctus.freqs | Mozart | Requiem Sanctus |
| Not Like Us.wav | Not Like Us.freqs | Unknown | Not Like Us |
| Playboi Carti - Crush.wav | Playboi Carti - Crush.freqs | Playboi Carti ft. Travis Scott | Crush |
| Playboi Carti - EVIL JORDAN.wav | Playboi Carti - EVIL JORDAN.freqs | Playboi Carti | Evil Jordan |
| Polo G - Darkside.wav | Polo G - Darkside.freqs | Polo G | Darkside |
| Quavo, Lil Baby - Legends.wav | Quavo, Lil Baby - Legends.freqs | Quavo, Lil Baby | Legends |
| Quinta Sinfonia - 1º movimento - Beethoven.wav | Quinta Sinfonia - 1º movimento - Beethoven.freqs | Beethoven | Symphony No. 5 - 1st Movement |
| Rainbow - I Surrender.wav | Rainbow - I Surrender.freqs | Rainbow | I Surrender |
| Travis Scott - FEIN ft. Playboi Carti.wav | Travis Scott - FEIN ft. Playboi Carti.freqs | Travis Scott ft. Playboi Carti | FEIN |
| Ultravox - All Stood Still.wav | Ultravox - All Stood Still.freqs | Ultravox | All Stood Still |
| Vangelis - Spiral.wav | Vangelis - Spiral.freqs | Vangelis | Spiral |
| XXXTENTACION & Juice WRLD - whoa.wav | XXXTENTACION & Juice WRLD - whoa.freqs | XXXTENTACION & Juice WRLD | Whoa (Mind in Awe) Remix |
| Young Thug - Money On Money.wav | Young Thug - Money On Money.freqs | Young Thug ft. Future | Money On Money |

##### Query Sample Mappings

| Sample File | Original Song |
|------------|---------------|
| sample01.wav | Rainbow - I Surrender |
| sample02.wav | Carlos Paredes - Canção Verdes Anos |
| sample03.wav | Ultravox - All Stood Still |
| sample04.wav | Mozart Requiem Sanctus |
| sample05.wav | Quinta Sinfonia - 1º movimento - Beethoven |
| sample06.wav | Vangelis - Spiral |
| sample07.wav | Metallica - The Memory Remains |

Note: 
- All original .wav files are stored in the `database/` directory
- Signature (.freqs) files are stored in `signatures/database/`
- Query samples are stored in `queries/` directory

### 3. Build the Signature Database

```bash
python3 scripts/setup_database.py
```

## Usage

### Generate Query Segments

```bash
python3 scripts/generate_queries.py
```

### Run Identification Experiments

```bash
python3 scripts/run_experiments.py --generate-plots
```

### Evaluate Results

```bash
python3 src/evaluation.py
```

## Customization

- **Change signature extraction parameters:**  
  See `scripts/setup_database.py` for options like `--win-size`, `--shift`, etc.
- **Test different compressors or noise levels:**  
  See `scripts/run_experiments.py` for `--compressors` and `--noise-levels` options.

## Results

- Results and plots are saved in the `results/` directory.
- Evaluation reports are generated as text files and CSVs.

## Troubleshooting

- **Missing dependencies:**  
  Ensure all Python packages and system tools (`sox`, `GetMaxFreqs`) are installed.
- **Audio file errors:**  
  Only use supported formats (`.wav`, `.flac`, `.mp3`).

## Authors

- Group 7, TAI Assignment 3

---