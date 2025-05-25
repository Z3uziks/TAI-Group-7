import os
import numpy as np
from music_identifier import MusicIdentifier
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from audio_processor import add_noise, extract_segment

def evaluate_compressor(compressor: str, music_dir: str, query_dir: str, results_dir: str):
    """Evaluate a specific compressor on the music identification task."""
    identifier = MusicIdentifier(compressor=compressor)
    
    # Build database
    print(f"Building database using {compressor}...")
    for music_file in os.listdir(music_dir):
        if music_file.endswith(('.wav', '.mp3')):
            music_path = os.path.join(music_dir, music_file)
            music_name = os.path.splitext(music_file)[0]
            identifier.add_to_database(music_path, music_name)
    
    # Test with clean queries
    print("Testing with clean queries...")
    clean_results = []
    for query_file in tqdm(os.listdir(query_dir)):
        if query_file.endswith(('.wav', '.mp3')):
            query_path = os.path.join(query_dir, query_file)
            true_name = os.path.splitext(query_file)[0]
            predicted_name, ncd = identifier.identify(query_path)
            clean_results.append({
                'true_name': true_name,
                'predicted_name': predicted_name,
                'ncd': ncd,
                'correct': true_name == predicted_name
            })
    
    # Test with noisy queries
    print("Testing with noisy queries...")
    noisy_results = []
    for query_file in tqdm(os.listdir(query_dir)):
        if query_file.endswith(('.wav', '.mp3')):
            query_path = os.path.join(query_dir, query_file)
            true_name = os.path.splitext(query_file)[0]
            
            # Create noisy version
            noisy_path = os.path.join(results_dir, f"noisy_{query_file}")
            add_noise(query_path, noisy_path)
            
            predicted_name, ncd = identifier.identify(noisy_path)
            noisy_results.append({
                'true_name': true_name,
                'predicted_name': predicted_name,
                'ncd': ncd,
                'correct': true_name == predicted_name
            })
            
            # Clean up
            os.remove(noisy_path)
    
    # Calculate and print results
    clean_accuracy = sum(r['correct'] for r in clean_results) / len(clean_results)
    noisy_accuracy = sum(r['correct'] for r in noisy_results) / len(noisy_results)
    
    print(f"\nResults for {compressor}:")
    print(f"Clean accuracy: {clean_accuracy:.2%}")
    print(f"Noisy accuracy: {noisy_accuracy:.2%}")
    
    return clean_results, noisy_results

def plot_results(results_dict: dict, output_path: str):
    """Plot comparison of results for different compressors."""
    compressors = list(results_dict.keys())
    clean_accuracies = [sum(r['correct'] for r in results_dict[c][0]) / len(results_dict[c][0])
                       for c in compressors]
    noisy_accuracies = [sum(r['correct'] for r in results_dict[c][1]) / len(results_dict[c][1])
                       for c in compressors]
    
    plt.figure(figsize=(10, 6))
    x = np.arange(len(compressors))
    width = 0.35
    
    plt.bar(x - width/2, clean_accuracies, width, label='Clean')
    plt.bar(x + width/2, noisy_accuracies, width, label='Noisy')
    
    plt.xlabel('Compressor')
    plt.ylabel('Accuracy')
    plt.title('Music Identification Accuracy by Compressor')
    plt.xticks(x, compressors)
    plt.legend()
    
    plt.savefig(output_path)
    plt.close()

def prepare_test_segments(music_dir: str, query_dir: str, segment_duration: float = 10.0):
    """
    Prepare test segments from music files.
    
    Args:
        music_dir: Directory containing full music files
        query_dir: Directory to save query segments
        segment_duration: Duration of each segment in seconds
    """
    os.makedirs(query_dir, exist_ok=True)
    
    for music_file in os.listdir(music_dir):
        if music_file.endswith(('.wav', '.mp3')):
            music_path = os.path.join(music_dir, music_file)
            base_name = os.path.splitext(music_file)[0]
            
            # Extract a segment from the middle of the file
            segment_path = os.path.join(query_dir, f"{base_name}_segment.wav")
            extract_segment(music_path, segment_path, 30.0, segment_duration)

def main():
    # Create necessary directories
    os.makedirs('results', exist_ok=True)
    
    # Prepare test segments
    prepare_test_segments('music_database', 'query_segments')
    
    # Test different compressors
    compressors = ['gzip', 'bzip2', 'lzma', 'zstd']
    results = {}
    
    for compressor in compressors:
        results[compressor] = evaluate_compressor(
            compressor,
            'music_database',
            'query_segments',
            'results'
        )
    
    # Plot results
    plot_results(results, 'results/compressor_comparison.png')

if __name__ == '__main__':
    main() 