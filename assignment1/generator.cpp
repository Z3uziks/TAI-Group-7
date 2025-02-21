#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cmath>
#include <vector>
#include <algorithm>

using namespace std;

class Generator {
    private:
    int k; // Markov order
    double alpha; // Smoothing parameter

    string prior; // Starting context
    int size; // Number of characters to generate

    unordered_map<string, unordered_map<char, int>> frequency_table;

    public:
    Generator(int k, double alpha, string prior, int size) {
        this->k = k;
        this->alpha = alpha;
        this->prior = prior;
        this->size = size;
    }

    void loadModel() {
        ifstream file("model.txt"); // Fixed filename for automatic reading
        if (!file) {
            cerr << "Error opening model file: model.txt" << endl;
            exit(1);
        }

        string line;
        while (getline(file, line)) {
            // load frequency table
        }
        file.close();
    }

    unordered_map<string, vector<pair<char, double>>> build_probability_table(unordered_map<string, unordered_map<char, int>> frequency_table, unordered_map<string, int> context_counts) {
        unordered_map<string, vector<pair<char, double>>> probability_table;
        for (auto const& [context, frequencies] : frequency_table) {
            vector<pair<char, double>> probabilities;
            int context_count = context_counts[context];

            for (auto const& [character, frequency] : frequencies) {
                double probability = (frequency + alpha) / (context_count + alpha * 26); // change 26 to the size of the alphabet
                probabilities.push_back(make_pair(character, probability));
            }
            probability_table[context] = probabilities;
        }
        return probability_table;
    }

    string generateText(unordered_map<string, vector<pair<char, double>>> probability_table) {
        string context = prior;
        string generatedText = context;
        
        for (int i = 0; i < size; i++) {
            vector<pair<char, double>> probabilities = probability_table[context];
            sort(probabilities.begin(), probabilities.end(), [](pair<char, double> a, pair<char, double> b) {
                return a.second > b.second;
            });

            double random = (double) rand() / RAND_MAX;
            double cumulative_probability = 0;
            char next_character;
            for (auto const& [character, probability] : probabilities) {
                cumulative_probability += probability;
                if (random < cumulative_probability) {
                    next_character = character;
                    break;
                }
            }

            generatedText += next_character;
            context = context.substr(1) + next_character;
        }
        
        return generatedText;
    }
    
    void saveToFile(const string &filename, const string &text) {
        ofstream outFile(filename);
        if (!outFile) {
            cerr << "Error opening output file: " << filename << endl;
            exit(1);
        }
        outFile << text;
        outFile.close();
        cout << "Generated text saved to " << filename << endl;
    }
};

int main(int argc, char *argv[]) {
    if (argc != 9) {
        cerr << "Usage: " << argv[0] << " -k <order> -a <alpha> -p <prior> -s <size>\n";
        return 1;
    }
    
    int k = stoi(argv[2]);
    double alpha = stod(argv[4]);
    string prior = argv[6];
    int size = stoi(argv[8]);
    
    if (prior.length() < k) {
        cerr << "Error: Prior context length must be at least " << k << " characters" << endl;
        return 1;
    }

    Generator generator(k, alpha, prior, size);
    generator.loadModel();
    
    string generatedText = generator.generateText();
    cout << "Generated Text: " << generatedText << endl;
    
    generator.saveToFile("generated_output.txt", generatedText);
    
    return 0;
}