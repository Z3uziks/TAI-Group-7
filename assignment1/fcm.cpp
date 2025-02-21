#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cmath>
#include <vector>
#include <algorithm>

using namespace std;

class FiniteContextModel {
private:
    int k; // Markov order
    double alpha; // Smoothing parameter
    unordered_map<string, int> context_counts;
    
    public:
    FiniteContextModel(int order, double smoothing) : k(order), alpha(smoothing) {}
    unordered_map<string, unordered_map<char, int>> frequency_table;

    void train(const string &text) {
        for (size_t i = 0; i + k < text.size(); ++i) {
            string context = text.substr(i, k);
            char next_symbol = text[i + k];
            
            frequency_table[context][next_symbol]++;
            context_counts[context]++;
        }
        cout << "Size: " << frequency_table.size() << endl;
    }

    double probability(const string &context, char symbol) {
        // if (context_counts.find(context) == context_counts.end())
        //     return 1.0 / 256; // Uniform probability for unseen contexts

        int count_symbol = frequency_table[context][symbol] + alpha;
        int count_context = context_counts[context] + alpha * 256;
        return static_cast<double>(count_symbol) / count_context;
    }

    double compute_entropy(const string &text) {
        double entropy = 0.0;
        for (size_t i = 0; i + k < text.size(); ++i) {
            string context = text.substr(i, k);
            char next_symbol = text[i + k];
            double prob = probability(context, next_symbol);
            entropy += log2(prob);
        }
        cout << "Entropy: " << entropy << endl;
        cout << "Text size: " << text.size() << endl;
        return -entropy / (text.size() - k);
    }
};

string read_file(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        exit(1);
    }

    string line;
    getline(file, line); // Skip the first line

    string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    return content;
}

void print_frequencyTable(const unordered_map<string, unordered_map<char, int>> &frequency_table) {
    string result;
    
    for (const auto &context : frequency_table) {
        if (context.first.find('\n') != string::npos) {
            string modified_context = context.first;
            replace(modified_context.begin(), modified_context.end(), '\n', '\\');
            result += modified_context + ": ";
        } else {
            result += context.first + ": ";
        }
        for (const auto &symbol : context.second) {
            if (symbol.first == '\n') {
                result += "\\n";
            } else {
                result += symbol.first;
            }
            result += " ";
            result += to_string(symbol.second);
            result += ", ";
        }
        result += "\n";
    }
    cout << result;
}

int main(int argc, char *argv[]) {
    if (argc != 6) {
        cerr << "Usage: " << argv[0] << " <input_file> -k <order> -a <alpha>\n";
        return 1;
    }
    
    string filename = argv[1];
    int k = stoi(argv[3]);
    double alpha = stod(argv[5]);
    
    string text = read_file(filename);

    FiniteContextModel fcm(k, alpha);
    fcm.train(text);
    print_frequencyTable(fcm.frequency_table);
    double entropy = fcm.compute_entropy(text);
    
    cout << "Average Information Content: " << entropy << " bps" << endl;
    return 0;
}
