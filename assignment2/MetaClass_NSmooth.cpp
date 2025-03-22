#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <cmath>
#include <future>
#include <chrono>

// Struct to hold organism information and NRC value
struct OrganismMatch {
    std::string name;
    double nrc;
    
    OrganismMatch(const std::string& n, double v) : name(n), nrc(v) {}
    
    bool operator<(const OrganismMatch& other) const {
        return nrc < other.nrc;
    }
};

// MarkovModel class for training and calculating NRC
class MarkovModel {
private:
    int k;                      // Context size
    double alpha;               // Smoothing parameter
    int alphabet_size;          // Size of the alphabet (4 for DNA: A, C, G, T)
    
    // Map for storing counts: context -> symbol -> count
    std::unordered_map<std::string, std::unordered_map<char, int>> counts;

public:
    MarkovModel(int context_size, double smoothing_param) : 
        k(context_size), 
        alpha(smoothing_param), 
        alphabet_size(4) {}
    
    // Train the model on a given sequence
    void train(const std::string& sequence) {
        for (size_t i = 0; i < sequence.length() - k; ++i) {
            std::string context = sequence.substr(i, k);
            char next_symbol = sequence[i + k];
            
            counts[context][next_symbol]++;
        }
    }
    
    // Estimate the number of bits needed to encode a sequence
    double estimate_bits(const std::string& sequence) {
        double compression_bits = 0.0;
        for (size_t i = 0; i <= sequence.size() - k; ++i) {
            std::string k2 = sequence.substr(i, k);
            auto it = counts.find(k2);
            compression_bits += (it != counts.end()) ? it->second.size() : log2(1);
        }
        return compression_bits;
    }
    
    // Calculate Normalized Relative Compression (NRC)
    double calculate_nrc(const std::string& sequence) {
        if (sequence.length() <= static_cast<std::string::size_type>(k)) {
            return 1.0;
        }
        
        double bits = estimate_bits(sequence);
        
        // NRC formula: C(x||y) / (|x| * log2(A))
        // For DNA, log2(A) = log2(4) = 2
        double nrc = bits / (2.0 * sequence.length());
        
        return nrc;
    }
};

// Function to read metagenomic sample from file
std::string read_metagenomic_sample(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        exit(1);
    }
    
    std::string sample;
    std::string line;
    
    while (std::getline(file, line)) {
        line.erase(std::remove_if(line.begin(), line.end(), ::isspace), line.end());
        sample += line;
    }
    
    file.close();
    return sample;
}

// Function to read reference database from file
std::vector<std::pair<std::string, std::string>> read_reference_database(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file " << filename << std::endl;
        exit(1);
    }
    
    std::vector<std::pair<std::string, std::string>> references;
    std::string current_name;
    std::string current_sequence;
    std::string line;
    
    while (std::getline(file, line)) {
        line.erase(std::remove_if(line.begin(), line.end(), ::isspace), line.end());
        
        if (!line.empty()) {
            if (line[0] == '@') {
                if (!current_name.empty()) {
                    references.push_back(std::make_pair(current_name, current_sequence));
                }
                
                // Start a new organism
                current_name = line.substr(1);  // Remove the '@' prefix
                current_sequence.clear();
            } else {
                current_sequence += line;
            }
        }
    }
    
    if (!current_name.empty()) {
        references.push_back(std::make_pair(current_name, current_sequence));
    }
    
    file.close();
    return references;
}

// Multi-threaded NRC calculation
std::vector<OrganismMatch> calculate_nrc_parallel(const std::vector<std::pair<std::string, std::string>>& reference_db, MarkovModel& model) {
    std::vector<std::future<OrganismMatch>> futures;
    
    for (const auto& entry : reference_db) {
        futures.push_back(std::async(std::launch::async, [&model, entry]() {
            double nrc = model.calculate_nrc(entry.second);
            return OrganismMatch(entry.first, nrc);
        }));
    }

    std::vector<OrganismMatch> results;
    for (auto& fut : futures) {
        results.push_back(fut.get());
    }

    return results;
}

// Function to save results to CSV
void save_results_to_csv(const std::vector<OrganismMatch>& results, int top) {
    std::ofstream outFile("results.csv");
    if (!outFile.is_open()) {
        std::cerr << "Error: Could not open results.csv for writing." << std::endl;
        return;
    }

    outFile << "Rank,NRC,Organism\n";
    for (int i = 0; i < std::min(top, static_cast<int>(results.size())); ++i) {
        outFile << i + 1 << "," << results[i].nrc << "," << results[i].name << "\n";
    }

    outFile.close();
    std::cout << "Results saved to results.csv" << std::endl;
}

// Function to display help message
void display_help() {
    std::cout << "MetaClass: Metagenome classification using NRC\n\n";
    std::cout << "Usage: MetaClass -d <database> -s <sample> [-k <context>] [-a <alpha>] [-t <top>]\n\n";
    std::cout << "Options:\n";
    std::cout << "  -d FILE   Path to the reference database file\n";
    std::cout << "  -s FILE   Path to the metagenomic sample file\n";
    std::cout << "  -k INT    Context size for Markov model (default: 10)\n";
    std::cout << "  -a FLOAT  Smoothing parameter (default: 0.1)\n";
    std::cout << "  -t INT    Number of top matches to display (default: 20)\n";
    std::cout << "  -h        Display this help message\n";
}

// Main function
int main(int argc, char* argv[]) {
    std::string db_file;
    std::string sample_file;
    int k = 10;
    double alpha = 0.1;
    int top = 20;
    
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        
        if (arg == "-h") {
            display_help();
            return 0;
        } else if (arg == "-d" && i + 1 < argc) {
            db_file = argv[++i];
        } else if (arg == "-s" && i + 1 < argc) {
            sample_file = argv[++i];
        } else if (arg == "-k" && i + 1 < argc) {
            k = std::stoi(argv[++i]);
        } else if (arg == "-a" && i + 1 < argc) {
            alpha = std::stod(argv[++i]);
        } else if (arg == "-t" && i + 1 < argc) {
            top = std::stoi(argv[++i]);
        } else {
            std::cerr << "Unknown option: " << arg << std::endl;
            display_help();
            return 1;
        }
    }
    
    if (db_file.empty() || sample_file.empty()) {
        std::cerr << "Error: Database and sample files are required.\n";
        display_help();
        return 1;
    }
    
    // Read the metagenomic sample
    std::cout << "Reading metagenomic sample from " << sample_file << "..." << std::endl;
    std::string metagenomic_sample = read_metagenomic_sample(sample_file);
    
    // Train a Markov model on the metagenomic sample
    std::cout << "Training Markov model with k=" << k << ", alpha=" << alpha << "..." << std::endl;
    MarkovModel model(k, alpha);
    model.train(metagenomic_sample);
    
    // Read the reference database
    std::cout << "Reading reference database from " << db_file << "..." << std::endl;
    auto reference_db = read_reference_database(db_file);
    std::cout << "Database contains " << reference_db.size() << " reference sequences." << std::endl;
    
    // Calculate NRC for each reference sequence
    std::cout << "Calculating NRC values..." << std::endl;
    auto start = std::chrono::high_resolution_clock::now();
    auto results = calculate_nrc_parallel(reference_db, model);
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end - start;
    std::cout << "Multi-threaded execution time: " << elapsed.count() << " seconds.\n";

    
    // Sort by NRC value (lower is better - indicates more compression)
    std::sort(results.begin(), results.end());
    
    // Print the top matches
    std::cout << "\nTop " << top << " matches:" << std::endl;
    std::cout << "----------------------------------------------------------" << std::endl;
    std::cout << "Rank  NRC        Organism" << std::endl;
    std::cout << "----------------------------------------------------------" << std::endl;
    
    int limit = std::min(top, static_cast<int>(results.size()));
    for (int i = 0; i < limit; ++i) {
        printf("%-5d %-10.4f %s\n", i+1, results[i].nrc, results[i].name.c_str());
    }

    // Save to CSV
    save_results_to_csv(results, top);
    
    return 0;
}