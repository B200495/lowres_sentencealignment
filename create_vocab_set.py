"""
Create vocab set by iterating through each dictionary entry and see if it can be found in the English text file. If found, keep in dict. If not found, eliminate from dict. Create a new dict object and pickle it rather than overwriting the original dict file.

Do this rather than creating a vocab set from English text then eliminating dictionary entries using the set as dict entries can span multiple words so you'd have to do a sliding window across the entire English text to create a vocab inventory.

Write to deal with a single chapter/text segment (.EOA-separated) then expand code to iterate through all.
Modify filepaths before running.
"""
import pickle
import string
import pyewts # converts Tib characters to Latin/Wylie transliteration (EWTS) and back.

#### Set filepaths and other constants ####
bookname = "vecaligntest"
filenum = "01"
total_parts = 1

# upper range limit should be 1 above actual number of parts
for filenum in range(1, total_parts+1):
    filenum = str(filenum).zfill(2)

    print(f"BOOK: {bookname}")
    print(f"PART {filenum}")

    # English novel .txt file path (not combinations, strict English sentences)
    eng_data_path = #ADD: e.g. f"./vecalign/{bookname}_src/ENG_sentences/ENG_{bookname}_{filenum}"

    valby_dict_path = #ADD: e.g. f"./dict_transl/jimvalby_dict.pickle"
    hopkins_dict_path = #ADD: e.g. f"./dict_transl/hopkins_dict.pickle"
    ives_dict_path = #ADD: e.g. f"./dict_transl/ives_dict.pickle"

    # top 500 English and Tibetan words frequency list filepath
    top500en_path = #ADD: e.g. f"./dict_transl/top500list_en.pickle" # list
    top500bo_path = #ADD: e.g. f"./dict_transl/top500bo.txt" # file - each line = a word

    # Pickle outfile paths
    valby_dict_outpath = #ADD: e.g. f"./dict_transl/{bookname}_dicts/jimvalby_dict_{bookname}_{filenum}.pickle"
    hopkins_dict_outpath = #ADD: e.g. f"./dict_transl/{bookname}_dicts/hopkins_dict_{bookname}_{filenum}.pickle"
    ives_dict_outpath = #ADD: e.g. f"./dict_transl/{bookname}_dicts/ives_dict_{bookname}_{filenum}.pickle"

    # instantiate Tib-->Wylie transliteration converter
    converter = pyewts.pyewts()

    #### HELPER FUNCTIONS ####

    def read_pickle(filepath):
        # Read the pickle object (dictionary) from the file
        with open(filepath, "rb") as file:
            my_dict = pickle.load(file)
        return my_dict

    def pickle_object(object_to_pickle, file_to_write_dotpickle):
        with open(file_to_write_dotpickle, 'wb') as file:
            # Pickle the item
            pickle.dump(object_to_pickle, file)


    def normalise_entry(entry):
        # remove punct and make lower-case. INPUT list element (string). OUTPUT modified string.
        entry = entry.translate(str.maketrans('', '', string.punctuation)).lower()
        return entry

    def is_partial_match(value, eng_text, threshold=0.8):
        """
        Helper function for use within word_in_dict. Ensures the term is in the Eng transl reference to enforce sensical copy behaviour by NMT model. If 80% (e.g. threshold) of the dictionary value (consecutive characters) is in english sentence (based on characters) then return True = match.
        INPUT: Value(str)= the dict entry in English for a given tibetan term. Eng_sent(str)= sentence to cross-reference with. Threshold = the %
        OUTPUT: True or False depending on whether deemed match or not.
        """
        value_length = len(value)
        match_length = int(value_length * threshold)

        for i in range(len(value)):
            substring = value[i:i + match_length]
            if len(substring) == match_length:
                if substring in eng_text:
                    return True
        return False

    #### Read entire English file into a single string, not \n-separated. ####

    with open(eng_data_path, 'r') as file:
        eng_data = file.read().replace('\n', ' ')

    # Remove commas and apostrophes from the string to maximise match chances
    eng_data = eng_data.replace(',', '').replace("'", '').lower()

    # print(eng_data)

    #### Read in all three dict pickle objects ####

    valby_dict = read_pickle(valby_dict_path)
    hopkins_dict = read_pickle(hopkins_dict_path)
    ives_dict = read_pickle(ives_dict_path)

    dict_list = [valby_dict, hopkins_dict, ives_dict]

    #### Read in top500en list and convert to set ####

    top500en = set(read_pickle(top500en_path))

    # print(top500en)

    #### Read in top500bo file and convert to set ####

    top500bo = []
    with open(top500bo_path, 'r') as file:
        for line in file:
            line = line.strip()
            # transliterate line
            line = converter.toWylie(line)
            top500bo.append(line)

    top500bo = set(top500bo)

    # normalise by removing punctuation to improve chances of matches
    top500en = {normalise_entry(entry) for entry in top500en}

    # print(top500en)

    #### Remove dict entries which match with top500en set objects ####

    # print(len(dict_list[0]))
    # print(len(dict_list[1]))
    # print(len(dict_list[2]))

    # Iterate through each dictionary
    for dictionary in dict_list:
        # Create a new dictionary to store the filtered entries
        new_dict = {}

        # Iterate through each key-value pair in the dictionary
        for key, value in dictionary.items():
            # Filter out entries that match the top500en set, normalising by removing entry punctuation to increase match chances
            # print(f"VALUE TO NORMALISE in {dictionary} (should be list of strings): {value}")
            filtered_value = [entry for entry in value if normalise_entry(entry) not in top500en]

            # # PRINT and Check if any entries were removed
            # if len(value) != len(filtered_value):
            #     removed_entries = [entry for entry in value if entry not in filtered_value]
            #     print(f"Removed entries from {key}: {removed_entries}")

            # Check if any entries remain after filtering
            if len(filtered_value) > 0:
                # Update the new dictionary with the filtered entries
                new_dict[key] = filtered_value

        # Replace the original dictionary with the filtered dictionary
        dictionary.clear()
        dictionary.update(new_dict)

    # Print the updated lengths of the dictionaries
    print(len(dict_list[0]))
    print(len(dict_list[1]))
    print(len(dict_list[2]))

    #### One dict at a time, iterate through each dict entry and search for it in the English file string. Match needs to ignore case (and punctuation?). If there's a match, keep in the dict. If there's a match, keep entry in dict. If no match, remove entry from dict. ####
    # Only want to include dict entries which are in the English text

    # One dict at a time...
    for dictionary in dict_list:
        # Create a new dictionary to store the filtered entries
        new_dict = {}

        # Iterate through each key-value pair in the dictionary
        for key, value in dictionary.items():
        # Filter out entries that are found in the English text, normalising by removing entry punctuation to increase match chances
            filtered_value = []
            for entry in value:
                if is_partial_match((" " + normalise_entry(entry) + " "), eng_data, threshold=0.9):
                # if (" " + normalise_entry(entry) + " ") in eng_data:
                    filtered_value.append(entry)

            # # PRINT and Check if any entries were removed
            # if len(value) != len(filtered_value):
            #     removed_entries = [entry for entry in value if entry not in filtered_value]
            #     print(f"Removed entries from {key}: {removed_entries}")

            # Check if any entries remain after filtering
            if len(filtered_value) > 0:
                # Update the new dictionary with the filtered entries
                new_dict[key] = filtered_value

        # Replace the original dictionary with the filtered dictionary
        dictionary.clear()
        dictionary.update(new_dict)

    print("After Eng filtering, before Tib filtering:")
    print(len(dict_list[0]))
    print(len(dict_list[1]))
    print(len(dict_list[2]))

    for dictionary in dict_list:
        new_dict_2 = {}
        # Iterate through each key-value pair in the dictionary
        for key, value in dictionary.items():
        # Filter out entries whose keys are found in the top500bo list to remove noise from later annotations (BO_novelannotate.py).
            if key not in top500bo:
                new_dict_2[key] = value
            # else:
            #     print(f"Removed word: {key}")

        dictionary.clear()
        dictionary.update(new_dict_2)

    print("After Tib filtering")
    print(len(dict_list[0]))
    print(len(dict_list[1]))
    print(len(dict_list[2]))


    #### Pickle new chapter/segment-specific dict object ####

    print("pickling new dicts")
    pickle_object(valby_dict, valby_dict_outpath)
    pickle_object(hopkins_dict, hopkins_dict_outpath)
    pickle_object(ives_dict, ives_dict_outpath)

    print("finished pickling")
