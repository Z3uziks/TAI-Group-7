#include <iostream>
#include <fstream>
#include <vector>
#include <cstdlib>

using namespace std;

vector<string> sequence_files = {"sequence1.txt", "sequence2.txt", "sequence3.txt", "sequence4.txt", "sequence5.txt"};
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
    vector<string> result_lines;
    while (fgets(buffer, sizeof(buffer), pipe) != NULL) {
        result_lines.push_back(buffer);
    }
    pclose(pipe);

    if (result_lines.size() >= 2) {
        string entropy_line = result_lines[result_lines.size() - 2];
        string aic_line = result_lines[result_lines.size() - 1];

        double entropy;
        double average_information_content;
        if (sscanf(entropy_line.c_str(), "Entropy: %lf bps", &entropy) == 1 &&
            sscanf(aic_line.c_str(), "Average Information Content: %lf bps", &average_information_content) == 1) {
            output_file << input_file << "," << k << "," << alpha << "," << average_information_content << "," << entropy << endl;
        }
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