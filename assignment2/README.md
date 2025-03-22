# MetaClass - Normalized Relative Compression for Metagenomics

MetaClass is a tool for analyzing metagenomic samples using Normalized Relative Compression (NRC). It identifies which known organisms from a reference database share the highest similarity with the genomes found in a metagenomic sample.

## Installation Instructions

### Prerequisites

Make sure you have the following installed on your Linux system:
- C++ compiler with C++11 support (g++ recommended)
- GNU Make

### Compilation

To compile all implementations at once, simply run:

```bash
make
```

This will build all three executables: `MetaClass`, `MetaClass_Simple`, and `MetaClass_NSmooth`.

To build specific implementations individually:

```bash
make standard    # Builds the standard implementation (MetaClass.cpp)
make simple      # Builds the simple implementation (MetaClass_C.cpp)
make nsmooth     # Builds the alternative smoothing implementation (MetaClass_NSmooth.cpp)
```

## Running the Program

### Basic Usage

```bash
./MetaClass -d db.txt -s meta.txt -k 10 -a 0.1 -t 20
```
**Note:** MetaClass_C doesn't have -a parameter (also for the MetaClass_NSmooth its not needed)
### Command Line Options

- `-d <file>`: Path to the reference database file (required)
- `-s <file>`: Path to the metagenomic sample file (required)
- `-k <int>`: Context size for Markov model (default: 10)
- `-a <float>`: Smoothing parameter (default: 0.1)
- `-t <int>`: Number of top matches to display (default: 20)
- `-h`: Display help message

### Example

```bash
./MetaClass -d db.txt -s meta.txt -k 8 -a 0.01 -t 10
```

This runs MetaClass with:
- `db.txt` as the reference database
- `meta.txt` as the metagenomic sample
- Context size of 8
- Smoothing parameter of 0.01
- Displaying the top 10 matches

## Available Implementations

The project includes three different implementations:

1. **Standard Implementation** (`MetaClass.cpp`): 
   - Full-featured implementation with multi-threading support
   - Detailed Markov model with proper Laplace smoothing
   - CSV output and detailed logging

2. **Simple Implementation** (`MetaClass_C.cpp`):
   - Simplified implementation with core functionality
   - Smaller codebase for easier understanding
   - Basic command-line interface

3. **Alternative Smoothing** (`MetaClass_NSmooth.cpp`):
   - Similar to the standard implementation but with an alternative compression calculation
   - Uses a different approach to context-based compression estimation

## How It Works

1. The program trains a finite-context model (Markov model) using only the metagenomic sample.
2. The model's counts are frozen after training.
3. For each sequence in the reference database:
   - The program estimates the amount of bits required to compress the sequence using the model.
   - It applies the Normalized Relative Compression (NRC) formula to measure similarity.
4. Results are sorted by NRC value (lower is better) and the top matches are displayed.

## NRC Formula

The Normalized Relative Compression (NRC) is calculated as:

```
NRC(x||y) = C(x||y) / (|x| * log₂(A))
```

Where:
- `C(x||y)` is the number of bits needed to compress sequence x using a model trained on sequence y
- `|x|` is the length of sequence x
- `log₂(A)` is the logarithm base 2 of the alphabet size (for DNA, A=4 so log₂(4)=2)

Lower NRC values indicate higher similarity between sequences.

## Output

The program outputs:
1. A ranked list of the top matches to the console
2. A CSV file (`results.csv`) containing the top matches for further analysis