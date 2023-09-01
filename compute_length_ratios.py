"""
Compute sentence length ratios between English and Tibetan lines in Latse7 test. Ratios to be used to find appropriate search window for sentence combination elimination method.
Modify filepaths before running.
"""
eng_path = #ADD: e.g. f"./latse7_testset/EN_latse7test"
bo_path = #ADD: e.g. f"./latse7_testset/BO_latse7test"

eng_line_count = 0
bo_line_count = 0

eng_char_count = 0
bo_char_count = 0

with open(eng_path, "r") as file:
    for line in file:
        eng_line_count += 1
        eng_char_count += len(line)

with open(bo_path, "r") as file:
    for line in file:
        bo_line_count += 1
        bo_char_count += len(line)

bo_avg_perline = bo_char_count/bo_line_count
eng_avg_perline = eng_char_count/eng_line_count

print(f"TOTAL: Tib line count = {bo_line_count}")
print(f"TOTAL: Tib character count = {bo_char_count}")
print(f"Average characters per line: {bo_avg_perline}")

print(f"TOTAL: Eng line count = {eng_line_count}")
print(f"TOTAL: Eng character count = {eng_char_count}")
print(f"Average characters per line: {eng_avg_perline}")

print(f"TIB:ENG character ratio per line = {bo_avg_perline}:{eng_avg_perline}")
