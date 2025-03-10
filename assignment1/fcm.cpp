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

    int getSigma(const string &text) {
        vector<char> symbols;
        for (char c : text) {
            if (find(symbols.begin(), symbols.end(), c) == symbols.end()) {
                symbols.push_back(c);
            }
        }

        return symbols.size();
    }

    void train(const string &text) {
        for (size_t i = 0; i + k < text.size(); ++i) {
            string context = text.substr(i, k);
            char next_symbol = text[i + k];
            
            frequency_table[context][next_symbol]++;
            context_counts[context]++;
        }
    }

    double probability(const string &context, char symbol, const int sigma) {
        
        int count_symbol = frequency_table[context][symbol] + alpha;
        int count_context = context_counts[context] + alpha * sigma;
        return static_cast<double>(count_symbol) / count_context;
    }
    
    
    double compute_aic(const string &text) {
        double entropy = 0.0;
        const int sigma = getSigma(text);
        for (size_t i = 0; i + k < text.size(); ++i) {
            string context = text.substr(i, k);
            char next_symbol = text[i + k];
            double prob = probability(context, next_symbol, sigma);
            entropy += log2(prob);
        }
        //
        return -entropy / (text.size() - k);
    }

    double compute_entropy(const string &text) {
        double entropy = 0.0;
        unordered_map<char, int> symbol_counts;
        
        for (char c : text) {
            symbol_counts[c]++;
        }

        for (const auto &entry : symbol_counts) {
            double prob = static_cast<double>(entry.second) / text.size();
            entropy += prob * log2(prob);
        }

        return -entropy;
    }

    void save_model(const string &filename) {
        ofstream file(filename);
        if (!file.is_open()) {
            cerr << "Error saving model to file: " << filename << endl;
            return;
        }
        file << k << " " << alpha << "\n";
        for (const auto &entry : frequency_table) {
            file << entry.first << " ";
            for (auto it = entry.second.begin(); it != entry.second.end(); ++it) {
            file << it->first << " " << it->second;
            if (next(it) != entry.second.end()) {
                file << " ";
            }
            }
            file << "\n";
        }
        file.close();
    };
};

string read_file(const string &filename) {
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error opening file: " << filename << endl;
        exit(1);
    }

    string line;
    // getline(file, line); // Skip the first line

    string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    return content;
}


void print_frequencyTable(const unordered_map<string, unordered_map<char, int>> &frequency_table) {
    cout << "{\n";
    for (const auto &context : frequency_table) {
        string mod_context = context.first;
        if (context.first.find('\n') != string::npos) {
            replace(mod_context.begin(), mod_context.end(), '\n', '\\');
        }
        cout << "  \"" << mod_context << "\": {\n";
        for (const auto &symbol : context.second) {
            cout << "    \"" << (symbol.first == '\n' ? "\\n" : string(1, symbol.first)) << "\": " << symbol.second << ",\n";
        }
        cout << "  },\n";
    }
    cout << "}\n";
}

void save_frequencyTable(const unordered_map<string, unordered_map<char, int>> &frequency_table) {
    ofstream file("frequency_table.txt");
    if (!file.is_open()) {
        cerr << "Error opening file: frequency_table.txt" << endl;
        exit(1);
    }

    for (const auto &context : frequency_table) {
        string mod_context = context.first;
        if (context.first.find('\n') != string::npos) {
            size_t pos = 0;
            while ((pos = mod_context.find('\n', pos)) != string::npos) {
                mod_context.replace(pos, 1, "\\n");
                pos += 2;
            }
        }
        file << mod_context << ":";
        bool first = true;
        for (const auto &symbol : context.second) {
            if (!first) {
            file << ";";
            }
            if (symbol.first == '\n') {
            file << "\\n;" << symbol.second;
            } else {
            file << symbol.first << ";" << symbol.second;
            }
            first = false;
        }
        file << "\n";
        }
        file.close();
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
    fcm.save_model("model.txt");
    double avg_info_content = fcm.compute_aic(text);
    double entropy = fcm.compute_entropy(text);

    
    
    
    cout << "Entropy: " << entropy << " bps" << endl;
    cout << "Average Information Content: " << avg_info_content << " bps" << endl;
    return 0;
}
