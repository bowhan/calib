//
// Created by borabi on 19/12/17.
//

#include "string"
#include <iostream>

#include "global.h"
#include "commandline.h"
#include "extract.h"
#include "cluster.h"

using namespace std;

ofstream dog;
ofstream node_dog;

int main(int argc, char *argv[]){
    parse_flags(argc, argv);

    dog = ofstream(output_prefix + "cluster.log");
    node_dog = ofstream(output_prefix + "cluster.node.log");
    print_flags(dog);

    if (!silent) {
        cout << "Extracting minimizers and barcodes...\n";
    }
    extract_barcodes_and_minimizers();


    if (!silent) {
        cout << "Clustering...\n";
    }
    cluster();
    if (!silent) {
        cout << "All done! Have a good day!\n";
    }
}
