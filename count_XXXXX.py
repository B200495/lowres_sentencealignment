"""
Use to count eliminated entries after novel annotation in cases where counter failed.

"""
import re

### CONSTANTS ###
bookname = "dragonthunder"
partnum = "01"
total_parts = 33

eliminatedlines_counter = 0

for partnum in range(1, total_parts+1):
    partnum = str(partnum).zfill(2)
    
    # FILEPATH: Modified Tibetan sentence combination file (overlap file)
    sentencecombofile = f"/work/tc046/tc046/s2252632/vecalign/{bookname}_src/BO_modified_sentence_combos/BO_{bookname}_{partnum}.bo"

    # load Tibetan sentence combos text file into LIST object
    data = []
    with open(sentencecombofile, "r") as file:
        # Read each line in the file into a LIST OBJECT
        for line in file:
            # Remove trailing newline character and append the line to the list
            data.append(line.rstrip('\n'))
            
    
    eliminated_lines = sum(1 for entry in data if re.search(r'XXXXX\d+', entry))
    print(f"{eliminated_lines} lines eliminated in BOOK {bookname} PART {partnum}")

    eliminatedlines_counter += eliminated_lines
    
print(f"TOTAL ELIMINATED LINES: {eliminatedlines_counter}")