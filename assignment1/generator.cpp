#include <iostream>
#include <fstream>
#include <unordered_map>
#include <cmath>
#include <vector>
#include <algorithm>
#include <sstream>
#include <unordered_set>

using namespace std;

class Generator {
private:
    int k; // Markov order
    double alpha; // Smoothing parameter
    string prior; // Starting context
    int size; // Number of characters to generate

    unordered_map<string, unordered_map<string, int>> frequency_table;
    unordered_map<string, int> context_counts;
    int unique_chars;

public:
    Generator(int k, double alpha, string prior, int size) {
        this->k = k;
        this->alpha = alpha;
        this->prior = prior;
        this->size = size;
    }

    void loadModel() {
        ifstream file("frequency_table.txt", ios::binary);
        if (!file) {
            cerr << "Error opening model file: frequency_table.txt" << endl;
            exit(1);
        }
    
        // Use a set to track all unique characters
        unordered_set<string> allUniqueChars;
    
        string line;
        while (getline(file, line)) {
            size_t colonPos = line.find(':');
            if (colonPos == string::npos) continue;
    
            string context = line.substr(0, colonPos);
            string pairsStr = line.substr(colonPos + 1);
    
            vector<string> tokens;
            {
                string token;
                istringstream tokenStream(pairsStr);
                while (getline(tokenStream, token, ';')) {
                    if (!token.empty()) tokens.push_back(token);
                }
            }
    
            int total_count = 0; // accumulate frequency counts
            for (size_t i = 0; i + 1 < tokens.size(); i += 2) {
                string str = tokens[i];  // 'str' can now be a single character or "\\n"
                int count = stoi(tokens[i + 1]);
                frequency_table[context][str] = count;
                total_count += count;
                allUniqueChars.insert(str);
            }
            context_counts[context] = total_count; // store total for this context
        }
        file.close();
    
        unique_chars = allUniqueChars.size(); // Set the number of unique characters
    }

    unordered_map<string, vector<pair<string, double>>> build_probability_table() {
        unordered_map<string, vector<pair<string, double>>> probability_table;
        for (auto const& [context, frequencies] : frequency_table) {
            vector<pair<string, double>> probabilities;
            int context_count = context_counts[context];

            for (auto const& [str, frequency] : frequencies) {
                double probability = (frequency + alpha) / (context_count + alpha * unique_chars); // change 26 to the size of the alphabet
                probabilities.push_back(make_pair(str, probability));
            }
            probability_table[context] = probabilities;
        }
        return probability_table;
    }

    string generateText(unordered_map<string, vector<pair<string, double>>> probability_table) {
        string context = prior;
        string generatedText = context;
        
        for (int i = 0; i < size; i++) {
            // Ensure the context length is valid
            if (context.empty()) {
                cerr << "Error: Context is empty! Exiting." << endl;
                break;
            }
    
            // Fetch the probabilities for the current context
            vector<pair<string, double>> probabilities = probability_table[context];
            if (probabilities.empty()) {
                cerr << "Error: No probabilities found for context '" << context << "'!" << endl;
                break;
            }
    
            sort(probabilities.begin(), probabilities.end(), [](pair<string, double> a, pair<string, double> b) {
                return a.second > b.second;
            });
    
            // Generate a random number and use it to select the next character or escape sequence
            double random = (double) rand() / RAND_MAX;
            double cumulative_probability = 0;
            string next_string;
    
            for (auto const& [str, probability] : probabilities) {
                cumulative_probability += probability;
                if (random < cumulative_probability) {
                    next_string = str; // We now store the whole string (could be a char or "\\n")
                    break;
                }
            }
    
            // Append the next "string" (could be a single char or "\\n") to the generated text
            generatedText += next_string;
    
            // Update the context (shift by one and append the new string)
            if (next_string == "\\n") {
                // If we generate "\\n", we need to keep the last token and move forward
                context = context.substr(1) + "\\n";  // Keep "\\n" as one token in the context
            } else {
                // Ensure that the context has at least `k` characters and update correctly
                if (static_cast<int>(context.length()) >= k) {
                    context = context.substr(1) + next_string;  // Shift the window and append the new string
                } else {
                    context += next_string;  // If context is shorter than `k`, just append the new string
                }
            }
        }
    
        return generatedText;
    }
    
    
    string computeText(const string& generatedText) {
        string processedText = generatedText;
        // Replace all occurrences of "\\n" with actual newlines
        size_t pos = 0;
        while ((pos = processedText.find("\\n", pos)) != string::npos) {
            processedText.replace(pos, 2, "\n");
            pos += 1; // Move past the replaced character
        }
        return processedText;
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

    if (prior.length() < static_cast<size_t>(k)) {
        cerr << "Error: Prior context length must be at least " << k << " characters" << endl;
        return 1;
    }

    Generator generator(k, alpha, prior, size);
    generator.loadModel();

    unordered_map<string, vector<pair<string, double>>> probability_table;
    probability_table = generator.build_probability_table();

    string generatedText = generator.generateText(probability_table);
    cout << "Generated Text (with '\\n' placeholders): " << generatedText << endl;

    // Compute and apply line breaks
    string processedText = generator.computeText(generatedText);
    cout << "Processed Text (with actual line breaks): " << endl << processedText << endl;

    // Save the processed text to file
    generator.saveToFile("generated_output.txt", processedText);

    return 0;
}
