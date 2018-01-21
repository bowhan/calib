//
// Created by borabi on 19/12/17.
//

#include "commandline.h"

using namespace std;

// Parameter definitions
string input_1 = "";
string input_2 = "";
string output_prefix = "";
bool silent = false;
bool keep_qual = false;
int barcode_length = -1;
int minimizer_count = -1;
int error_tolerance = -1;
int minimizer_threshold = -1;
int thread_count = 1;
int kmer_size = -1;

void parse_flags(int argc, char *argv[]){
    for (int i = 0; i < argc; i++) {
        string current_param(argv[i]);
        if (current_param == "-f" || current_param == "--input-forward") {
            input_1 = string(argv[i+1]);
        }
        if (current_param == "-r" || current_param == "--input-reverse") {
            input_2 = string(argv[i+1]);
        }
        if (current_param == "-o" || current_param == "--output-prefix") {
            output_prefix = string(argv[i+1]);
        }
        if (current_param == "-s" || current_param == "--silent") {
            silent = true;
        }
        if (current_param == "-q" || current_param == "--keep-qual") {
            keep_qual = true;
        }
        if (current_param == "-l" || current_param == "--barcode-length") {
            barcode_length = atoi(argv[i+1]);
        }
        if (current_param == "-m" || current_param == "--minimizer-count") {
            minimizer_count = atoi(argv[i+1]);
        }
        if (current_param == "-k" || current_param == "--kmer-size") {
            kmer_size = atoi(argv[i+1]);
        }
        if (current_param == "-e" || current_param == "--error-tolerance") {
            error_tolerance = atoi(argv[i+1]);
        }
        if (current_param == "-t" || current_param == "--minimizer-threshold") {
            minimizer_threshold = atoi(argv[i+1]);
        }
        if (current_param == "-c" || current_param == "--threads") {
            thread_count = atoi(argv[i+1]);
        }
    }

    if (barcode_length < 0 || minimizer_count < 0 || error_tolerance < 0 || minimizer_threshold < 0 || kmer_size < 0) {
        cout << "Missing parameters!\n";
        exit(-1);
    }
    if (input_1 == "" || input_2 == "" || output_prefix == "") {
        cout << "Missing parameters!\n";
        exit(-1);
    }
    if (thread_count < 1 || thread_count > 8) {
        cout << "Thread count must be between 1 and 8!\n";
        exit(-1);
    }
    if (minimizer_threshold > minimizer_count || minimizer_threshold < 1) {
        cout << "Minimizer threshold must be <= minimizer count and >= 1\n";
        exit(-1);
    }
}

void print_flags(ofstream &out){
    out << "Parameters:\n";
    out << "\tinput_1:\t" << input_1 << "\n";
    out << "\tinput_2:\t" << input_2 << "\n";
    out << "\toutput_prefix:\t" << output_prefix << "\n";
    out << "\tbarcode_length:\t" << barcode_length << "\n";
    out << "\tminimizer_count:\t" << minimizer_count << "\n";
    out << "\tkmer_size:\t" << kmer_size << "\n";
    out << "\terror_tolerance:\t" << error_tolerance << "\n";
    out << "\tminimizer_threshold:\t" << minimizer_threshold << "\n";
    out << "\tthreads:\t" << thread_count << "\n";

}
// void print_flags(ofstream &out){
//
// }
