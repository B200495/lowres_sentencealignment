"""
Script annotates Tibetan with English bilingual dictionary annotations ('Method 3').
Modify filepaths before running.
"""

import datasets # HuggingFace module
from botok import Text # tokenises Tibetan words, with some mistakes
import pickle # to load pickled dictionaries (preprocessed/formatted)
import pyewts # converts Tib characters to Latin/Wylie transliteration (EWTS) and back.
# import nltk # for Eng tokenisation
import string # for Eng tokenisation
import random # so we can randomly ignore some dict matches
import re # to fix weird 'o+o' pattern encoding which doubles vowels in dict lookup after Tib --> Wylie conversion, identify dict annotations crossing newline boundaries in english window
import sys # for flushing output to terminal for progress updates and in case of premature slurm job cancellation

### CONSTANTS ###
bookname = "vecaligntest"
partnum = "01"
total_parts = 1

eliminatedlines_counter = 0

for partnum in range(1, total_parts+1):
    partnum = str(partnum).zfill(2)

    # num of eng characters to tibetan characters, computed from manually aligned test set (Latse7-test)
    eng2tib_ratio = 0.76

    # FILEPATH: Tibetan novel .txt file (cleaned, not yet aligned - COMBINATIONS)
    novel_filepath = #ADD: e.g. f"./vecalign/{bookname}_src/sentence_combos/BO_{bookname}_{partnum}.bo"

    # FILEPATH: English novel .txt file (not combinations, strict English sentences)
    eng_data_path = #ADD: e.g. f"./vecalign/{bookname}_src/ENG_sentences/ENG_{bookname}_{partnum}"

    # FILEPATH: Output modified Tibetan sentence combination file (overlap file)
    output_sentencecombo = #ADD: e.g. f"./vecalign/{bookname}_src/BO_modified_sentence_combos/BO_{bookname}_{partnum}.bo"

    # ALTER DICT PATHS during full run to use full dicts, not minidicts. Dicts are book and book-part specific.
    valby_dict_path = #ADD: e.g. f"./dict_transl/{bookname}_dicts/jimvalby_dict_{bookname}_{partnum}.pickle"
    hopkins_dict_path = #ADD: e.g. f"./dict_transl/{bookname}_dicts/hopkins_dict_{bookname}_{partnum}.pickle"
    ives_dict_path = #ADD: e.g. f"./dict_transl/{bookname}_dicts/ives_dict_{bookname}_{partnum}.pickle"

    # load Tibetan sentence combos text file
    data = []
    with open(novel_filepath, "r") as file:
        # Read each line in the file into a LIST OBJECT
        for line in file:
            # Remove trailing newline character and append the line to the list
            data.append(line.rstrip('\n'))

    # load English in as a long string:
    with open(eng_data_path, 'r') as file:
        eng_data = file.read()
        # eng_data = file.read().replace('\n', ' ')


    # instantiate Tib-->Wylie transliteration converter
    converter = pyewts.pyewts()

    # random_ignore_threshold = X% chance of returning the match for a given dict match
    random_ignore_threshold=0.5

    ### FUNCTIONS ###

    def read_pickle(filepath):
        # Read the pickle object (dictionary) from the file
        with open(filepath, "rb") as file:
            my_dict = pickle.load(file)
        return my_dict

    # def normalise_english(eng_sent):
    #     # Tokenise, remove punct and lower-case an Eng sentence (TL)
    #     # Tokenize the sentence
    #     tokens = nltk.word_tokenize(eng_sent)

    #     # Remove punctuation
    #     tokens = [token for token in tokens if token not in string.punctuation]

    #     # Convert tokens to lowercase
    #     tokens = [token.lower() for token in tokens]
    #     return tokens

    def is_partial_match(tib_word, tib_sent, threshold=0.8):
        """
        Helper function for use within word_in_dict. Ensures the term is in the Eng transl reference to enforce sensical copy behaviour by NMT model. If 80% (e.g. threshold) of the dictionary value (consecutive characters) is in english sentence (based on characters) then return True = match.
        INPUT: Value(str)= the dict entry in English for a given tibetan term. Eng_sent(str)= sentence to cross-reference with. Threshold = the %
        OUTPUT: True or False depending on whether deemed match or not.
        """
    #     value_length = len(tib_word)
    #     match_length = int(value_length * threshold)

    #     for i in range(len(tib_word)):
    #         substring = value[i:i + match_length]
    #         if len(substring) == match_length:
    #             if substring in tib_sent:
    #                 return True
    #     return False
        value_length = len(tib_word)
        match_length = int(value_length * threshold)

        for i in range(len(tib_word) - match_length + 1):
            substring = tib_word[i:i + match_length]
            if substring.lower() in tib_sent.lower():
                return True
        return False

    def words_in_dict(tib_sentence, merged_dict):
        """INPUTS:
        tib_sentence: the Tibetan sentence you want to annotate (string)
        dict[123]: dictionaries you'll use to annotate the sentence (dict objects), refined to contain only relevant terms
        OUTPUT: tuple containing a list of english annotations (strings) AND a list of the tibetan terms with the eng annotations following them for debugging.
        """
        annotations = [] # just english words
        annotated_sent = [] # mix of eng and tib words

        o_pattern = r'o\+o'
        i_pattern = r'i\+i'
        e_pattern = r'e\+e'
        a_pattern = r'a\+a'
        u_pattern = r'u\+u'

        transliterated_sent = converter.toWylie(tib_sentence)
        transliterated_sent = re.sub(o_pattern, 'o', transliterated_sent)
        transliterated_sent = re.sub(i_pattern, 'i', transliterated_sent)
        transliterated_sent = re.sub(e_pattern, 'e', transliterated_sent)
        transliterated_sent = re.sub(a_pattern, 'a', transliterated_sent)
        transliterated_sent = re.sub(u_pattern, 'u', transliterated_sent)
        transliterated_sent = transliterated_sent.rstrip()
        # print(f"Tib sent: {tib_sentence}\nTransliterated sent: {transliterated_sent}") # COMMENT OUT AFTER DEBUGGING

        annotations_set = set(annotations)

        for key, value in merged_dict.items():
            # key is tibetan, values are english in dicts
            # values are lists of strings
            if key in transliterated_sent:
                annotations_set.update(value)

        return (annotations, annotated_sent)

    def window(char_seq, window_size=100):
        """
        Sliding window code to slide across
        Char_seq = input string to have window slide across.
        Window_size = num of characters in window.
        Outputs one character sequence at a time - generator object? Use list comprehension to print in full but this will be unecessarily computationally expensive.
        """
        window_size = int(window_size)
        for i in range(len(char_seq) - window_size + 1):
            yield char_seq[i:i+window_size]

    ### CODE ###

    valby_dict = read_pickle(valby_dict_path)
    hopkins_dict = read_pickle(hopkins_dict_path)
    ives_dict = read_pickle(ives_dict_path)

    # merge dicts

    merged_dict = {}
    merged_dict.update(valby_dict)
    merged_dict.update(hopkins_dict)
    merged_dict.update(ives_dict)

    try:
        del merged_dict['ho'] # this entry kept on popping up and I don't understand why (wylie 'ho' wasn't in the sentence transliteration but still matched(?) even on partial matchthreshold 1)
    except:
        print("no 'ho' key to remove")

    print(f"Merged dict length: {len(merged_dict)}")

    # # add speechmarks to dict as extra match clue
    # merged_dict['“'] = ['“', '"']
    # merged_dict['”'] = ['”', '"']
    # merged_dict['"'] = ['”', '“']

    ## Some extra dict cleaning:

    #Remove list entries starting with a dash (-)
    merged_dict = {k: [item for item in v if not item.startswith('-')] for k, v in merged_dict.items()}

    #Remove list entries starting with a ('(')
    merged_dict = {k: [item for item in v if not item.startswith('(')] for k, v in merged_dict.items()}

    #Remove list entries ending with a (')')
    merged_dict = {k: [item for item in v if not item.endswith(')')] for k, v in merged_dict.items()}

    # Remove list entries with fewer than 3 characters
    merged_dict = {k: [item for item in v if len(item) >= 3] for k, v in merged_dict.items()}

    # Remove dictionary entries with empty lists as values
    merged_dict = {k: v for k, v in merged_dict.items() if v}

    # lower-case english string to increase match chances
    lowercase_eng = eng_data.lower()

    # list to record eliminated lines
    eliminated = []
    x_counter = 1

    for i, sentencecombo_line in enumerate(data):
        if i % 1000 == 0:
                print(f"Processing line {i} of {len(data)}")
        # data = a list of tibetan line entries (overlap file entries)
        if sentencecombo_line == "PAD": # no need to annotate PAD line
            continue
        else:
            # remove blank spaces to facilitate search
            sentencecombo_line_spacecleared = sentencecombo_line.replace(' ', '')


            annotations, annotated_sent = words_in_dict(sentencecombo_line_spacecleared, merged_dict)
            # remove duplications obtained from multiple dict entry matches
            annotations = set(annotations)

            # print(f"Annotations: {annotations}")
            # print(f"Annotated sentence: {annotated_sent}\n")

            # eng_toks = normalise_english(eng_sent)

            ### Set search window within English text ###

            combo_len = len(sentencecombo_line)
            eng_scaledequiv = combo_len * eng2tib_ratio

            # increase search window by 10% to account for slight differences from the norm and \n characters
            eng_search_window = eng_scaledequiv * 1.1
            # print(f"combo_len: {combo_len}")
            # print(f"eng_scaledequiv: {eng_scaledequiv}")
            # print(f"eng search window: {eng_search_window}")

            ### Search in English for exact annotation matches within search window of defined character length for this given overlap file line ###

            for seq in window(lowercase_eng, eng_search_window):
                # return True if ALL annotation items are in the returned windowed sequence (seq)
                annotations = list(annotations)
                if len(annotations) > 1: # if there are 2+ annotations for the given sentence combination
                    # if all annotations feature in the English extract window
                    if all([annotation in seq for annotation in annotations]):
                        # print(f"Found a match...\nAnnotations: {annotations}\nWindow: {seq} ")

                        # check whether any two annotations are separated by a \n character
                        annotations_listed = str('[' + '|'.join(annotations) + ']')
                        regex_pattern = fr".*{annotations_listed}{{1}}.*\n.*{annotations_listed}{{1}}.*"

                        # if there's a match with this pattern then annotations are separated by \n so should be 'eliminated' from sentence combo file
                        if re.search(regex_pattern, seq):
                            print(f"eliminate match: {sentencecombo_line}\n")
                            eliminated.append(sentencecombo_line)
                            data[i] = "XXXXX" + str(x_counter)
                            x_counter += 1

                        # if no annotations are newline-separated in English..
                        else:
                            # print(f"allowable combo line: {sentencecombo_line}")
                            # leave sentencecombo_line unmodified and move to next line under consideration
                            # we found our match in the English text and have decided that this is a credible combination
                            break

    # print(len(data))

    for i, sentencecombo_line in enumerate(data):
        for elim_inst in eliminated:
            if elim_inst not in sentencecombo_line:
                continue
            else:
                data[i] = "XXXXX" + str(x_counter)
                x_counter += 1

    # print(len(data))

    # eliminated_lines = data.count('XXXXX')
    eliminated_lines = sum(1 for entry in data if re.search(r'XXXXX\d+', entry))

    print(f"BOOK: {bookname}\nPARTNUM{partnum}\n ELIMINATED LINES: {eliminated_lines}\n")

    with open(output_sentencecombo, "w") as file:
        for sentence_combo in data:
            file.write(str(sentence_combo) + "\n")

    print(f"finished {bookname} PART {partnum}")
    eliminatedlines_counter += eliminated_lines

    # Flush the output to ensure it is written to the terminal immediately
    sys.stdout.flush()

print("completely finished annotating")
print(f"total lines eliminated in {bookname}: {eliminatedlines_counter}")

### SYNONYMS: Could add code which tokenises the Tibetan combo line (use botok). For botok token, if Tibetan token has been annotated, continue. Else, if hasn't been annotated yet but it is in the text, it means the English dict entries (values) for that Tibetan word didn't match any English words in the passage. For these words, search for synonyms which are in the English passage. If you find something, this is an additional annotation.
