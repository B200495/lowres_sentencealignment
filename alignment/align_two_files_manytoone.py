#!
### FUNCTIONS ###

def picklines(thefile, whatlines):
    """
    INPUT: An open file-like object and a sorted list of zero-based line indices (whatlines)
    OUTPUT: A list, with low memory footprint and reasonable speed.
    """
    return [x for i, x in enumerate(thefile) if i in whatlines]


### CONSTANTS ###
book="vecaligntest"

total_parts = 1

# num="01"

for i in range(1, total_parts + 1):
    num = str(i).zfill(2)

    # original alignment files
    # alignment_file = ADD FILEPATH

    # modified many to one
    alignment_file = #ADD MANYTOONE ALIGNMENT FILEPATH - e.g.:
    # alignment_file = f"./vecalign/{book}_src/manytoone_aligns_ogtiboverlap/aligned_{num}_raw.txt"

    # modify below filepaths:
    # the preprocessed/cleaned source language text filepath:
    sl_file = #ADD: e.g. f"./vecalign/{book}_src/BO_{book}_{num}"
    # the preprocessed/cleaned target language text filepath:
    tl_file = #ADD: e.g. f"./vecalign/{book}_src/ENG_sentences/ENG_{book}_{num}"

    # OUTPUT filepaths:
    source_aligned_file = #ADD: e.g. f"./vecalign/{book}_src/manytoone_aligned/BO_{book}_al_{num}.txt"
    target_aligned_file = #ADD: e.g. f"./vecalign/{book}_src/manytoone_aligned/ENG_{book}_al_{num}.txt"

    ### CODE ###

    source_lines_list = []
    target_lines_list = []

    with open(alignment_file, "r") as file:
        for line in file:
            line = line.strip()
            target_lines = line.split("[")[1].split("]")[0].split(",")
            source_lines = line.split("[")[2].split("]")[0].split(",")

            # Convert source_lines to integers
            source_lines = [int(num) for num in source_lines if num.strip()]

            # Convert target_lines to integers
            target_lines = [int(num) for num in target_lines if num.strip()]

            source_lines_list.append(source_lines)
            target_lines_list.append(target_lines)

    # Remove empty entries in target_lines_list and corresponding entries in source_lines_list
    source_lines_list = [source_lines for source_lines, target_lines in zip(source_lines_list, target_lines_list) if target_lines]
    target_lines_list = [target_lines for target_lines in target_lines_list if target_lines]

    # Remove empty entries in source_lines_list and corresponding entries in target_lines_list
    target_lines_list = [target_lines for target_lines, source_lines in zip(target_lines_list, source_lines_list) if source_lines]
    source_lines_list = [source_lines for source_lines in source_lines_list if source_lines]

    print("Source Lines:")
    print(source_lines_list)

    print("\nTarget Lines:")
    print(target_lines_list)

    with open(sl_file, "r") as sl_f, open(tl_file, "r") as tl_f, open(source_aligned_file, "w") as source_aligned_f, open(target_aligned_file, "w") as target_aligned_f:
        for source_line_nums, target_line_nums in zip(source_lines_list, target_lines_list):
            # each element of zip obj = ([],[]) = LINE in new alignment files. source_lines now a LIST of line indices. same for target_lines.
            # Reset the file pointers to the beginning of the files
            sl_f.seek(0)
            tl_f.seek(0)

            # get LIST of relevant lines according to indices for this line
            collected_sourcelines_forpair = picklines(sl_f, source_line_nums)
            print(collected_sourcelines_forpair)
            collected_sourcelines_forpair = [item.strip() for item in collected_sourcelines_forpair]
            srcline_to_write = " ".join(collected_sourcelines_forpair).strip()
            source_aligned_f.write(srcline_to_write.strip() + "\n")

            collected_tgtlines_forpair = picklines(tl_f, target_line_nums)
            print(collected_tgtlines_forpair)
            collected_tgtlines_forpair = [item.strip() for item in collected_tgtlines_forpair]
            tgtline_to_write = " ".join(collected_tgtlines_forpair).strip()
            target_aligned_f.write(tgtline_to_write.strip() + "\n")

print("\nfinished aligning")
