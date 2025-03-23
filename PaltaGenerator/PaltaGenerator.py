from itertools import permutations


def generate_perm(word_length, p_file):
    p_file.writelines("\nWord Length:\t\t" + str(word_length) + "\n")
    octave_note_len = 8
    simple_scale = list(["S", "R", "G", "M", "P", "D", "N"])
    len_scale = len(simple_scale)
    scale_index = list(range(0, len_scale))
    p_list = list(permutations(scale_index, word_length))
    p_file.writelines("Combinations:\t\t" + str(2*len(p_list)) + "\n")
    for each_p in p_list:
        asc_palta = desc_palta = ""
        formula_set = list()
        tmp = each_p[0]
        for each_index in each_p:
            formula_set.append(each_index - tmp)
        p_file.writelines("\nFormula:\t\t" + str(formula_set) + "\n")
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
        p_file.writelines("Ascending:\t\t"+asc_palta + "\n")
        p_file.writelines("Descending:\t\t"+desc_palta + "\n")


def main():
    p_file = open('GeneratedPaltas.txt', 'w')
    generate_perm(2, p_file)
    generate_perm(3, p_file)
    generate_perm(4, p_file)
    generate_perm(5, p_file)
    generate_perm(6, p_file)
    generate_perm(7, p_file)
    p_file.close()


if __name__ == "__main__":
    main()
