"""
Script to piece together line-for-line alignments based on filenames for vecalign augmentation method2. If the Tibetan overlap file which generated the alignment contained 0 or ALL eliminated lines, use the original baseline vecalignment in its place.
Modify filepaths before running.
"""
import re

#### FUNCTIONS ####

def count_eliminations(bookname, tiboverlapfile, linenum):
    """
    tiboverlapfile = path to file in which to count eliminations
    OUTPUT: tuple containing (number of eliminated lines, elimination status)
    elimination_status = "all_eliminated" if all eliminated (all XXXX), "nothing_eliminated" if no lines eliminated, "fine" if everything fine)
    """
    eliminatedlines_counter = 0

    # load Tibetan sentence combos text file into LIST object
    data = []
    with open(tiboverlapfile, "r") as file:
        # Read each line in the file into a LIST OBJECT
        for line in file:
            # Remove trailing newline character and append the line to the list
            data.append(line.rstrip('\n'))


    eliminated_lines = sum(1 for entry in data if re.search(r'XXXXX\d+', entry))

    if eliminated_lines == 0:
        elimination_status = "nothing_eliminated"
    elif eliminated_lines == len(data):
        elimination_status = "all_eliminated"
    else:
        elimination_status = "fine"

    print(f"{eliminated_lines} lines eliminated in BOOK {bookname} LINE {linenum} - STATUS: {elimination_status}")

    return (eliminated_lines, elimination_status)

def read_file(filepath):
    """ Reads file line-by-line into list object """
    data_list = []
    with open(filepath, 'r') as in_file:
        for line in in_file:
            data_list.append(line)
    return data_list

#### CONSTANTS ####
book="vecaligntest"

total_lines = 221

alignedtext_outfile_eng = #ADD: e.g. f"./vecalign/{book}_src/method2_finalalignment/ENG_method2_finalalignment_{book}"

alignedtext_outfile_bo = #ADD: e.g. f"./vecalign/{book}_src/method2_finalalignment/BO_method2_finalalignment_{book}"

#### CODE ####

replacement_counter = 0
zero_all_elims_counter = 0
replacement_indices = [] # raw lines from OG alignment file to replace method2 alignments.
replacement_line_indices = [] # raw line indices for later processing for precision/recall/F1 metrics

for i in range(0, total_lines + 1):
    # num = line_num
    num = str(i)

    # read in as list objects but these will both be lists containing a SINGLE ITEM
    # MODIFY THESE PATHS
    eng_alignment_text = read_file(#ADD: e.g. f"./vecalign/{book}_src/method2_alignedfiles/ENG_{book}_al_01_line{num}.txt")
    bo_alignment_text = read_file(#ADD: e.g. f"./vecalign/{book}_src/method2_alignedfiles/BO_{book}_al_01_line{num}.txt")

    # MODIFY THIS PATHS
    # overlap file to check num eliminations in
    bo_overlap_file = #ADD: e.g. f"./vecalign/{book}_src/BO_modified_sentence_combos_perline/part_01/BO_{book}_01_line{num}.bo"

    # MODIFY THESE PATHS
    # OG vecalign many-to-1 alignment TEXT
    og_bo_alignment = read_file(#ADD: e.g. f"./vecalign/{book}_src/manytoone_aligned/BO_{book}_al_01.txt")
    og_eng_alignment = read_file(#ADD: e.g. f"./vecalign/{book}_src/manytoone_aligned/ENG_{book}_al_01.txt")

    # OG vecalign many-to-1 alignment INDICES
    og_alignment_inds = read_file(#ADD: e.g. f"./vecalign/{book}_src/manytoone_aligns/aligned_01_raw.txt")
    og_alignment_inds = [item.strip() for item in og_alignment_inds]

    new_en_alignmentlist = []
    new_bo_alignmentlist = []

    eliminated_lines, elimination_status = count_eliminations(book, bo_overlap_file, num)

    five_percent = len(bo_overlap_file) * .05

    if elimination_status in ["all_eliminated", "nothing_eliminated"]:
        ### annotation eliminations were unhelpful for vecalign and provide no clues so use original baseline vecalign alignment (manyto1).
        new_en_alignmentlist.append(og_eng_alignment[int(num)])
        new_bo_alignmentlist.append(og_bo_alignment[int(num)])

        replacement_indices.append(og_alignment_inds[int(num)])
        replacement_line_indices.append(int(num))

        replacement_counter += 1
        zero_all_elims_counter += 1

    elif eliminated_lines < five_percent:
        ### annotation eliminations were unhelpful for vecalign and provide no clues so use original baseline vecalign alignment (manyto1).
        new_en_alignmentlist.append(og_eng_alignment[int(num)])
        new_bo_alignmentlist.append(og_bo_alignment[int(num)])

        replacement_indices.append(og_alignment_inds[int(num)])
        replacement_line_indices.append(int(num))

        replacement_counter += 1

    else:
        new_en_alignmentlist.append(eng_alignment_text[0])
        new_bo_alignmentlist.append(bo_alignment_text[0])

    with open(alignedtext_outfile_eng, 'a') as out_file:
        for item in new_en_alignmentlist:
            out_file.write(item)
    with open(alignedtext_outfile_bo, 'a') as out_file:
        for item in new_bo_alignmentlist:
            out_file.write(item)

print("finished file creation\n")

print(f"{(zero_all_elims_counter/total_lines)*100}% line overlap files are unhelpful. {100-((zero_all_elims_counter/total_lines)*100)}% have potentially helpful amount of elimination.")
print(f"replaced {replacement_counter} of {total_lines} lines with original baseline (many-to-1).\n {(replacement_counter/total_lines)*100}% final alignment lines replaced in the end, so {100-((replacement_counter/total_lines)*100)}% were contributed by augmentation method 2.")

print(replacement_indices)
print(replacement_line_indices)
