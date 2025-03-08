#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>

using namespace std;

vector<string> sequence_files = {"sequence1.txt", "sequence2.txt"};
vector<int> k_values = {1, 2, 3, 4, 5};
vector<double> alpha_values = {0.01, 0.1, 1.0};

void run_fcm(const string &input_file, int k, double alpha, ofstream &output_file) {
    string command = "./fcm sequences/" + input_file + " -k " + to_string(k) + " -a " + to_string(alpha);
    cout << "Running: " << command << endl;
    
    FILE *pipe = popen(command.c_str(), "r");
    if (!pipe) {
        cerr << "Error running fcm" << endl;
        return;
    }
    
    char buffer[128];
    string result;
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result += buffer;
    }
    pclose(pipe);

    double entropy;
    double average_information_content;
    if (sscanf(result.c_str(), "Entropy: %lf bps\nAverage Information Content: %lf bps", &entropy, &average_information_content) == 2) {
        output_file << input_file << "," << k << "," << alpha << "," << average_information_content << "," << entropy << endl;
    }
}

int main() {
    ofstream output_file("aic_results.csv");
    if (!output_file.is_open()) {
        cerr << "Error opening output file" << endl;
        return 1;
    }
    output_file << "File,k,Alpha,AIC,Entropy" << endl;

    for (const auto &file : sequence_files) {
        for (int k : k_values) {
            for (double alpha : alpha_values) {
                run_fcm(file, k, alpha, output_file);
            }
        }
    }
    
    output_file.close();
    cout << "Results saved to aic_results.csv" << endl;
    return 0;
}