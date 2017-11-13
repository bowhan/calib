import sys
import pprint
import numpy as np
from itertools import islice, combinations
_complements = {'A': 'T',
                'T': 'A',
                'G': 'C',
                'C': 'G'}


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


def main():
    _barcode_length = 10
    _error_tolerance = 2
    barcodes_1 = []
    barcodes_2 = []
    reads1_file = open(sys.argv[1])
    while True:
        lines = [line for line in islice(reads1_file, 4)]
        if len(lines) < 4:
            break
        barcodes_1.append(lines[1][0:_barcode_length])
    reads1_file.close()
    reads2_file = open(sys.argv[2])
    while True:
        lines = [line for line in islice(reads2_file, 4)]
        if len(lines) < 4:
            break
        barcodes_2.append(lines[1][0:_barcode_length])
    reads2_file.close()
    if not len(barcodes_1) == len(barcodes_2):
        print('You messed up; the read files are not the same length')
        sys.exit(42)

    # lsh_1 = {}
    # lsh_2 = {}
    lsh = {}
    for barcode_num in range(len(barcodes_1)):
        for template, template_id in template_generator(_barcode_length, _error_tolerance):
            # TODO: Figure out if barcode list number should be attached to barcode number before inserting as a key
            barcode_1 = barcodes_1[barcode_num]
            barcode_1_rev = reverse_complement(barcode_1)
            barcode_2 = barcodes_2[barcode_num]
            barcode_2_rev = reverse_complement(barcode_2)
            barcode_1 = template(barcode_1)
            barcode_1_rev = template(barcode_1_rev)
            barcode_2 = template(barcode_2)
            barcode_2_rev = template(barcode_2_rev)

            new_key = str(template_id) + barcode_1 + barcode_2
            lsh[new_key] = lsh.get(new_key, {barcode_num}).union({barcode_num})
            new_key = str(template_id) + barcode_2_rev + barcode_1_rev
            lsh[new_key] = lsh.get(new_key, {barcode_num}).union({barcode_num})



    # for key, value in lsh_2.items():
    #     print(key, len(value), sep='\t')
    barcode_clusters = [{i} for i in range(len(barcodes_1))]
    # barcode_clusters_2 = [{i} for i in range(len(barcodes_2))]
    for barcode_set in lsh.values():
        union_set = set()
        for barcode in barcode_set:
            union_set.update(barcode_clusters[barcode])
        for barcode in union_set:
            barcode_clusters[barcode] = union_set
    # for barcode_set in lsh_2.values():
    #     union_set = set()
    #     for barcode in barcode_set:
    #         union_set.update(barcode_clusters_2[barcode])
    #     for barcode in union_set:
    #         barcode_clusters_2[barcode] = union_set
    # barcode_intersect_cluster = [{i} for i in range(len(barcodes_1))]
    # for barcode_num in range(len(barcode_intersect_cluster)):
    #     union_set = barcode_clusters_1[barcode_num].intersection(barcode_clusters_2[barcode_num])
    #     union_set.update(barcode_intersect_cluster[barcode_num])
    #     for barcode in union_set:
    #         barcode_intersect_cluster[barcode] = union_set
    # for barcode in range(len(barcode_intersect_cluster)):
    #     barcode_intersect_cluster[barcode] = barcode_clusters_1[barcode].intersection(barcode_clusters_2[barcode])

    id_dict = {}
    for _set in barcode_clusters:
        id_dict[id(_set)] = _set
    lines_1 = open(sys.argv[1]).readlines()
    lines_2 = open(sys.argv[2]).readlines()
    print(len(id_dict))
    for _set in id_dict.values():
        if len(_set) > 0:
            # reads = sorted(list(_set))
            # for l in [lines_1[i*4] for i in reads]:
            #    print(l[0:40])
            print(len(_set), sep='\t')


if __name__ == '__main__':
    main()
