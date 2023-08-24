def generate_perm(word_length):
    from itertools import permutations, combinations
    octave_note_len = 8
    simple_scale = list(["S", "R", "G", "M", "P", "D", "N"])
    len_scale = len(simple_scale)
    scale_index = list(range(0, len_scale))
    p_list = list(permutations(scale_index, word_length))
    print("Combinations: ", 2*len(p_list))
    for each_p in p_list:
        asc_palta = desc_palta = ""
        formula_set = list()
        tmp = each_p[0]
        for each_index in each_p:
            formula_set.append(each_index - tmp)
        print("\nFormula:\t", formula_set)
        for i in range(0, octave_note_len):
            for j in range(0, word_length):
                asc_palta = asc_palta + \
                    simple_scale[(i+formula_set[j]) % len_scale]
                desc_palta = desc_palta + \
                    simple_scale[(i-formula_set[j]) % len_scale]
            asc_palta = asc_palta + " "
            desc_palta = desc_palta + " "
        asc_palta = asc_palta + "-" + asc_palta[::-1]
        desc_palta = desc_palta + "-" + desc_palta[::-1]
        print("Ascending :\t", asc_palta)
        print("Descending :\t", desc_palta)


def main():
    print("\n--------Word Length: 2--------\n")
    generate_perm(2)
    print("\n--------Word Length: 3--------\n")
    generate_perm(3)
    print("\n--------Word Length: 4--------\n")
    generate_perm(4)
    print("\n--------Word Length: 5--------\n")
    generate_perm(5)
    print("\n--------Word Length: 6--------\n")
    generate_perm(6)
    print("\n--------Word Length: 7--------\n")
    generate_perm(7)


if __name__ == "__main__":
    main()
