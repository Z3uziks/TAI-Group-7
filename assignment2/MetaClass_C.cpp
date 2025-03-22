#include <iostream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <cmath>
#include <algorithm>

using namespace std;

const int ALPHABET_SIZE = 4; // A, C, G, T → log2(4) = 2
int kmer_size = 10;  // Default k-mer size

// Function to read the reference database (db.txt)
unordered_map<string, string> read_reference_db(const string &filename) {
    unordered_map<string, string> sequences;
    ifstream file(filename);
    if (!file) {
        cerr << "Error: Unable to open " << filename << endl;
        exit(1);
    }

    string line, id, seq;
    while (getline(file, line)) {
        if (line.empty()) continue;

        if (line[0] == '@') {  
            if (!id.empty() && !seq.empty()) {  
                sequences[id] = seq;  
            }
            id = line.substr(1);
            seq.clear();
        } else {
            seq += line;
        }
    }
    if (!id.empty() && !seq.empty()) {
        sequences[id] = seq;  
    }

    file.close();

    if (sequences.empty()) {
        cerr << "Error: No valid sequences found in " << filename << endl;
        exit(1);
    }

    return sequences;
}

// Function to read the metagenomic sample (meta.txt)
string read_metagenomic_sample(const string &filename) {
    ifstream file(filename);
    if (!file) {
        cerr << "Error: Unable to open " << filename << endl;
        exit(1);
    }

    string sample, line;
    while (getline(file, line)) {
        if (!line.empty()) sample += line;
    }
    
    file.close();

    if (sample.empty()) {
        cerr << "Error: Metagenomic sample is empty in " << filename << endl;
        exit(1);
    }

    return sample;
}

// Markov Model: k-mer frequency table
unordered_map<string, int> train_markov_model(const string &sample) {
    unordered_map<string, int> kmer_counts;
    int total_kmers = 0;

    for (size_t i = 0; i <= sample.size() - kmer_size; ++i) {
        string kmer = sample.substr(i, kmer_size);
        kmer_counts[kmer]++;
        total_kmers++;
    }

    for (auto &[kmer, count] : kmer_counts) {
        count = log2(count + 1); // Smoothing
    }

    return kmer_counts;
}

// Compression Estimation using Markov Model
double estimate_compression(const string &sequence, const unordered_map<string, int> &model) {
    double compression_bits = 0.0;
    for (size_t i = 0; i <= sequence.size() - kmer_size; ++i) {
        string kmer = sequence.substr(i, kmer_size);
        auto it = model.find(kmer);
        compression_bits += (it != model.end()) ? it->second : log2(1);
    }
    return compression_bits;
}

// Compute NRC
double compute_NRC(const string &sequence, const unordered_map<string, int> &model) {
    double C_x_given_y = estimate_compression(sequence, model);
    return C_x_given_y / (2 * sequence.size());
}

// Main function
int main(int argc, char *argv[]) {
    if (argc < 5) {
        cerr << "Usage: " << argv[0] << " -d db.txt -s meta.txt -k 10 -t 20" << endl;
        return 1;
    }

    string db_file, sample_file;
    int top_matches = 20;

    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "-d" && i + 1 < argc) db_file = argv[++i];
        else if (arg == "-s" && i + 1 < argc) sample_file = argv[++i];
        else if (arg == "-k" && i + 1 < argc) kmer_size = stoi(argv[++i]);
        else if (arg == "-t" && i + 1 < argc) top_matches = stoi(argv[++i]);
    }

    // Load data
    cout << "Loading reference database..." << endl;
    auto db_sequences = read_reference_db(db_file);

    cout << "Loading metagenomic sample..." << endl;
    string metagenomic_sample = read_metagenomic_sample(sample_file);

    cout << "Training Markov Model on metagenomic sample..." << endl;
    auto markov_model = train_markov_model(metagenomic_sample);

    // Compute NRC for each sequence in database
    vector<pair<string, double>> nrc_scores;
    cout << "Computing NRC scores..." << endl;
    for (const auto &[id, sequence] : db_sequences) {
        double nrc = compute_NRC(sequence, markov_model);
        nrc_scores.emplace_back(id, nrc);
    }

    // Sort by NRC (lower is better)
    sort(nrc_scores.begin(), nrc_scores.end(), [](const auto &a, const auto &b) {
        return a.second < b.second;
    });

    // Output top matches
    cout << "\nTop " << top_matches << " Matches:\n";
    for (int i = 0; i < min(top_matches, (int)nrc_scores.size()); ++i) {
        cout << i + 1 << ". " << nrc_scores[i].first << " (NRC: " << nrc_scores[i].second << ")\n";
    }

    return 0;
}
