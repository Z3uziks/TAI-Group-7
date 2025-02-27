#include <iostream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <random>
#include <algorithm>

using namespace std;

class FiniteContextModel {
private:
    int k;
    double alpha;
    unordered_map<string, int> context_counts;
    
    public:
    FiniteContextModel(int order, double smoothing) : k(order), alpha(smoothing) {}
    unordered_map<string, unordered_map<char, int>> frequency_table;

    void load_model(const string &filename) {
        ifstream file(filename, ios::binary);
        if (!file.is_open()) {
            cerr << "Error opening model file: " << filename << endl;
            exit(1);
        }
        file >> k >> alpha;
        file.ignore(); // Ignore newline after reading k and alpha
        string context;
        char c1, c2;
        while (file.get(c1) && file.get(c2)) {
            file.get(); // Ignore space
            context = string(1, c1) + string(1, c2);
            cout << "Context: " << context << endl;
            char symbol;
            // file.get(symbol);
            // cout << "Symbol: " << symbol << endl; 
            int count;
            while (file.get(symbol) && file >> count) {
                frequency_table[context][symbol] = count;
                context_counts[context] += count;
                cout << symbol << " " << count << endl;
                if (file.peek() == '\n') {
                    file.ignore(); // Ignore newline
                    cout << "Peeked newline" << endl;
                    break;
                }
                file.get();
            }
        }
        file.close();
    }

    char generate_next_symbol(const string &context) {
        if (frequency_table.find(context) == frequency_table.end()) {
            return ' '; // Default space for unknown contexts
        }

        vector<pair<char, int>> candidates(frequency_table[context].begin(), frequency_table[context].end());
        int total = context_counts[context];

        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<int> dist(0, total - 1);
        int rand_val = dist(gen);

        int sum = 0;
        for (const auto &entry : candidates) {
            sum += entry.second;
            if (rand_val < sum) {
                return entry.first;
            }
        }
        return ' ';
    }

    string generate_text(const string &initial_context, int length) {
        string generated_text = initial_context;
        for (int i = 0; i < length; ++i) {
            string context = generated_text.substr(generated_text.size() - k, k);
            char next_char = generate_next_symbol(context);
            generated_text += next_char;
        }
        return generated_text;
    }
};

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

int main(int argc, char *argv[]) {
    if (argc != 6) {
        cerr << "Usage: " << argv[0] << " <model_file> -p <prior> -s <length>\n";
        return 1;
    }
    
    string model_file = argv[1];
    string prior = argv[3];
    int sequence_length = stoi(argv[5]);
    
    FiniteContextModel fcm(0, 0.0);
    fcm.load_model(model_file);
    print_frequencyTable(fcm.frequency_table);
    
    string generated_text = fcm.generate_text(prior, sequence_length);
    cout << "Generated Text: " << generated_text << endl;
    
    ofstream output_file("generated_output.txt");
    if (!output_file.is_open()) {
        cerr << "Error opening output file: generatedOutput.txt" << endl;
        return 1;
    }
    output_file << generated_text;
    output_file.close();
    
    return 0;
}