import sys
import time
import statistics
import numpy as np
import math
from itertools import combinations
from igraph import Graph, summary, InternalError
import argparse

_complements = {'A': 'T',
                'T': 'A',
                'G': 'C',
                'C': 'G'}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clusters barcodes by locality sensitive hashing.")
    parser.add_argument("-f", "--forward-reads", type=str, help="Forward read file path.", required=True)
    parser.add_argument("-r", "--reverse-reads", type=str, help="Reverse read file path.", required=True)
    parser.add_argument("-l", "--barcode-length", type=int, default=10,
                        help="Barcode length (default: 10)")
    parser.add_argument("-e", "--error-tolerance", type=int, default=2,
                        help="Error tolerance for barcode clustering (default: 2)")
    parser.add_argument("-o", "--log-file", help="Log file path.", required=True)
    args = parser.parse_args()
    return args


def template_generator(barcode_size, error_tolerance):
    template_id = 0
    for comb in combinations(range(barcode_size), barcode_size - error_tolerance):
        def template(barcode):
            return ''.join([barcode[i] for i in comb])
        yield template, template_id
        template_id += 1


def reverse_complement(sequence):
    new_seq = ""
    for char in reversed(sequence):
        new_seq += _complements.get(char, char)
    return new_seq


def get_barcodes(fastq_file, barcode_length):
    fastq = open(fastq_file)
    barcodes = []
    EOF = False
    read_is_next = False
    while not EOF:
        line = fastq.readline()
        if read_is_next:
            barcodes.append(line[0:barcode_length])
            read_is_next = False
        if line.startswith("@"):
            read_is_next = True
        if line == "":
            EOF = True
    fastq.close()
    return barcodes


def get_barcode_pair_to_line_mapping(barcode_lines_1, barcode_lines_2):
    barcode_pair_to_line_dict = dict()
    for line in range(len(barcode_lines_1)):
        barcode_pair = (barcode_lines_1[line], barcode_lines_2[line])
        if barcode_pair in barcode_pair_to_line_dict:
            barcode_pair_to_line_dict[barcode_pair].add(line)
        else:
            barcode_pair_to_line_dict[barcode_pair] = {line}
    return barcode_pair_to_line_dict


def breadth_first_traversal(graph, node, cluster):
    cluster.add(node)
    nodes_to_traverse = graph[node] - cluster
    cluster.update(graph[node])
    for node in nodes_to_traverse:
        cluster.update(breadth_first_traversal(graph, node, cluster))
    return cluster


def generate_clusters_by_bfs(graph):
    # graph is a dict, clusters is an array of sets
    clusters = []
    for node in graph.keys():
        node_already_in_clusters = False
        for cluster in clusters:
            if node in cluster:
                node_already_in_clusters = True
                cluster.update(graph[node])
                break
        if not node_already_in_clusters:
            clusters.append(breadth_first_traversal(graph, node, set()))
    return clusters


def get_lsh(barcodes, error_tolerance):
    barcode_length = len(barcodes[0])
    # From AAAAAAAA, AAAAAAAT, ..., TTTTTTTT, ..., CCCCCCCC, ..., GGGGGGGG
    # lsh = np.array([set()]*(4**(barcode_length-error_tolerance)))
    # TODO: Implement this without hashing using the above method
    lsh = {}
    for template, template_id in template_generator(barcode_length, error_tolerance):
        for index in range(len(barcodes)):
            barcode_word = template(barcodes[index])
            lsh[barcode_word] = lsh.get(barcode_word, {index}).union({index})
    return lsh


def get_adjacency_set(lsh, num_barcodes):
    # TODO: Once get_lsh is implemented without hashing, change function to use list instead of dictionary
    adjacency_sets = np.array([set()] * num_barcodes)
    for adjacent_elements in lsh.values():
        for node in adjacent_elements:
            adjacency_sets[node].update(lsh.values)
    return adjacency_sets


def nCr(n, r):
    f = math.factorial
    return int(f(n) / f(r) / f(n-r))


def main():
    args = parse_args()

    _barcode_length = args.barcode_length
    _error_tolerance = args.error_tolerance

    log_file = open(args.log_file, 'w+')
    print('Hmmmm. Good morning?!', file=log_file)
    print('Step: Extracting barcodes...', file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    barcode_lines_1 = get_barcodes(args.forward_reads, _barcode_length)
    barcode_lines_2 = get_barcodes(args.reverse_reads, _barcode_length)
    if not len(barcode_lines_1) == len(barcode_lines_2):
        log_file = open(args.log_file, 'a')
        print('\tYou messed up; the read files are not of the same length', file=log_file)
        if not log_file == sys.stdout:
            log_file.close()
        sys.exit(42)
    barcode_pairs_to_lines = get_barcode_pair_to_line_mapping(barcode_lines_1, barcode_lines_2)

    log_file = open(args.log_file, 'a')
    print('\tTotal number of unique barcode pairs:', len(barcode_pairs_to_lines), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()

    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()

    log_file = open(args.log_file, 'a')
    print('Step: Storing reverse complement of barcodes...', file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    barcodes_1 = ['']*len(barcode_pairs_to_lines)
    barcodes_2 = ['']*len(barcode_pairs_to_lines)
    barcodes_rev_compl_1 = ['']*len(barcode_pairs_to_lines)
    barcodes_rev_compl_2 = ['']*len(barcode_pairs_to_lines)

    for index, barcode_pair in enumerate(barcode_pairs_to_lines.keys()):
        barcodes_1[index] = barcode_pair[0]
        barcodes_2[index] = barcode_pair[1]
        barcodes_rev_compl_1[index] = reverse_complement(barcode_pair[0])
        barcodes_rev_compl_2[index] = reverse_complement(barcode_pair[1])

    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    log_file = open(args.log_file, 'a')
    print('Step: LSH of barcodes...', file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    lsh_list = [{} for _ in range(int(nCr(_barcode_length, _error_tolerance)))]
    fake_barcode = ''.join([chr(x+65) for x in range(_barcode_length)])

    barcode_graph_adjacency_sets_test = [{read_id} for read_id in range(len(barcode_pairs_to_lines))]
    for template, template_id in template_generator(_barcode_length, _error_tolerance):
        log_file = open(args.log_file, 'a')
        lsh = lsh_list[template_id]
        print("\tTemplate {} with ID {}".format(template(fake_barcode), template_id), file=log_file)
        if not log_file == sys.stdout:
            log_file.close()
        for barcode_num in range(len(barcodes_1)):
            barcode_1 = template(barcodes_1[barcode_num])
            barcode_1_rev = template(barcodes_rev_compl_1[barcode_num])
            barcode_2 = template(barcodes_2[barcode_num])
            barcode_2_rev = template(barcodes_rev_compl_2[barcode_num])

            new_key = barcode_1 + barcode_2
            lsh[new_key] = lsh.get(new_key, {barcode_num}).union({barcode_num})
            barcode_graph_adjacency_sets_test[barcode_num].update(lsh[new_key])
            new_key = barcode_2_rev + barcode_1_rev
            lsh[new_key] = lsh.get(new_key, {barcode_num}).union({barcode_num})
            barcode_graph_adjacency_sets_test[barcode_num].update(lsh[new_key])


    log_file = open(args.log_file, 'a')
    print('\tThere are {} buckets with values in the LSH dictionaries'.format(sum((len(lsh.keys()) for lsh in lsh_list))), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    log_file = open(sys.argv[3] + '.supp', 'w+')
    print('Step: Counting the size of each set in LSH dictionaries...', file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    count = 0
    log_file = open(sys.argv[3] + '.supp', 'a')
    for lsh in lsh_list:
        for _set in lsh.values():
            print(len(_set), _set, sep='\t', file=log_file)
            count += 1
            if count == 100000:
                count = 0
                if not log_file == sys.stdout:
                    log_file.close()
                log_file = open(sys.argv[3] + '.supp', 'a')
    if not log_file == sys.stdout:
        log_file.close()
    finish_time = time.time()
    log_file = open(sys.argv[3] + '.supp', 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    log_file = open(args.log_file, 'a')
    print("Step: Building barcode graph adjacency sets...", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    barcode_graph_adjacency_sets = [{x} for x in range(len(barcode_pairs_to_lines))]
    count = 0
    for lsh in lsh_list:
        for val in lsh.values():
            count += 1
            if count % 100000 == 0:
                log_file = open(sys.argv[3], 'a')
                print('Count', count, file=log_file)
                log_file.close()
            for node in val:
                adjacent_nodes = val#.difference({node})
                barcode_graph_adjacency_sets[node].update(adjacent_nodes)
    for i in range(len(barcode_pairs_to_lines)):
        if barcode_graph_adjacency_sets[i] != barcode_graph_adjacency_sets_test[i]:
            print(barcode_graph_adjacency_sets_test[i], barcode_graph_adjacency_sets[i])

    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    log_file = open(args.log_file, 'a')
    print("Step: Building barcode graph from adjacency_sets...", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    barcode_graph = Graph([(node, neighbor) for node, neighbors in enumerate(barcode_graph_adjacency_sets) for neighbor in neighbors])
    log_file = open(args.log_file, 'a')
    print("\tGraph is building from adjacency lists is completed", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()

    barcode_graph.vs['id'] = [x for x in range(len(barcode_pairs_to_lines))]
    log_file = open(args.log_file, 'a')
    print("\tLabeling vertices on graph is completed", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()

    barcode_graph.simplify()
    log_file = open(args.log_file, 'a')
    print("\tSimplifying the graph is completed", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()

    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    log_file = open(args.log_file, 'a')
    print("Step: Getting clusters (connected components) of the barcode graph...", file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    start_time = time.time()

    cc_count = 0
    for connected_component in barcode_graph.clusters().subgraphs():
        cc_count += 1
        log_file = open(args.log_file, 'a')
        print('===\nDensity: {} and vertices:'.format(connected_component.density()), file=log_file)
        for barcode in connected_component.vs['id']:
            print(barcodes_1[barcode], barcodes_2[barcode], file=log_file)
        log_file.close()
    log_file = open(args.log_file, 'a')
    print('\tThere total of {} connected components'.format(cc_count), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()
    finish_time = time.time()
    log_file = open(args.log_file, 'a')
    print('\tLast step took {} seconds'.format(finish_time - start_time), file=log_file)
    if not log_file == sys.stdout:
        log_file.close()


if __name__ == '__main__':
    main()
