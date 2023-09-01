#!
"""
Read in and format dictionary files then save as pickle object.

Dict format:

{"'a 'bus": ['i'], "'a 'dogs": ["consonants with the letter 'a subscribed", "syllables with the vowel elongated by the addition of the letter 'a"], "'a 'ur": ['loud whirring noise'], "'a las": ['pah', 'bah', 'pooh'], "'a ma": ['but; but', 'yet', 'well']}

Keys = dict terms TIBETAN (Wylie-transliterated)
Values = list containing comma-separated ENGLISH terms/translations

Modify filepaths before running.
"""
import re
import pickle

# path of dict .txt file to be proceressed
jamesvalby = #ADD: e.g. f"./dict_transl/tibetan-dictionary/_input/dictionaries/public/07-JimValby"
dictname = "07-JimValby"

hopkins = #ADD: e.g. f"./dict_transl/tibetan-dictionary/_input/dictionaries/public/01-Hopkins2015"
ives = #ADD: e.g. f"./dict_transl/tibetan-dictionary/_input/dictionaries/public/08-IvesWaldo"

# lines_to_read = 40  # Number of lines to read while debugging


def pickle_file(pickle_file_path, dict_obj):
    """ Save the dictionary as a pickle object """
    with open(pickle_file_path, "wb") as file:
        pickle.dump(dict_obj, file)


def remove_trailing_chars(dictionary):
    """
    Removes a trailing '/' or '.' or './' from a list entry in a dict
    """
    for key, value in dictionary.items():
        # Check if the value is a list
        if isinstance(value, list):
            # Remove trailing characters from each list entry
            updated_value = [entry.rstrip('/').rstrip('.').lstrip('./').rstrip('/ ').rstrip('/. ').lstrip('./') for entry in value]
            dictionary[key] = updated_value
    return dictionary


####### JIM VALBY / JAMES VALBY #####

jim_dictionary = {}

with open(jamesvalby, "r", encoding="utf-8") as file:
    for line_num, line in enumerate(file, start=1):
        line = line.strip()
        if "|" in line:
            key, value = line.split("|", 1)

            value_list = [v.strip() for v in value.split(",")]

            # Jim Valby dict uses SA to list Tibetan synonyms - remove these entries for now. Could refer to them in future.
            if 'SA ' not in value:
                jim_dictionary[key] = value_list

        # if line_num >= lines_to_read:
        #     break

# Removing keys with no entries
jim_dictionary = {k: v for k, v in jim_dictionary.items() if v}

print("JIM VALBY\n")
# print(jim_dictionary)

# Path to save the pickle file
jim_pickle_file_path = #ADD: e.g. f"./dict_transl/jimvalby_dict.pickle"


####### HOPKINS ######

hopkins_dictionary = {}

with open(hopkins, "r", encoding="utf-8") as file:
    for line_num, line in enumerate(file, start=1):
        line = line.strip()
        if "|" in line:
            key, value = line.split("|", 1)

            value_list = [v.strip() for v in value.split(";")]

            # Remove bracketed content from values
            for i in range(len(value_list)):
                # Remove content enclosed in round brackets
                value_list[i] = re.sub(r'\([^()]*\)', '', value_list[i])
                # Remove content enclosed in square brackets
                value_list[i] = re.sub(r'\[[^\[\]]*\]', '', value_list[i])

            # Filter out empty entries from the list
            value_list = [v.strip() for v in value_list if v]

            # Jim Valby dict uses SA to list Tibetan synonyms - remove these entries for now. Could refer to them in the future.
            if 'SA ' not in value:
                hopkins_dictionary[key] = value_list

        # if line_num >= lines_to_read:
        #     break

# Removing keys with no entries
hopkins_dictionary = {k: v for k, v in hopkins_dictionary.items() if v}

print("\nHOPKINS\n")
# print(hopkins_dictionary)

# Path to save the pickle file
hopkins_pickle_file_path = "hopkins_dict.pickle"


####### IVES WALDO ######

ives_dictionary = {}

with open(ives, "r", encoding="utf-8") as file:
    for line_num, line in enumerate(file, start=1):
        line = line.strip()
        if "|" in line:
            key, value = line.split("|", 1)

            value_list = [v.strip() for v in value.split(";")]

            # Split list entries based on number followed by ')'
            split_value_list = []
            for entry in value_list:
                split_entries = re.split(r'\d+\)', entry)
                split_value_list.extend([e.strip() for e in split_entries if e.strip()])

                # Remove content enclosed in curly brackets and square brackets
                for i in range(len(split_value_list)):
                    # Remove content enclosed in curly brackets along with the brackets
                    split_value_list[i] = re.sub(r'\{[^{}]*\}', '', split_value_list[i])
                    # Remove content enclosed in square brackets along with the brackets
                    split_value_list[i] = re.sub(r'\[[^\[\]]*\]', '', split_value_list[i])

            # Jim Valby dict uses SA to list Tibetan synonyms - remove these entries for now. Could refer to them in future.
            if 'SA ' not in value:
                ives_dictionary[key] = split_value_list

            # Filter out empty entries from the list
            value_list = [v.strip() for v in value_list if v]

        # if line_num >= lines_to_read:
        #     break

# Removing keys with no entries
ives_dictionary = {k: v for k, v in ives_dictionary.items() if v}
ives_dictionary = remove_trailing_chars(ives_dictionary)

print("\nIVES\n")
# print(ives_dictionary)

# Path to save the pickle file
ives_pickle_file_path = #ADD: e.g. f"./dict_transl/ives_dict.pickle"


####### PICKLE DICTIONARY OBJECT ######

pickle_file(jim_pickle_file_path, jim_dictionary)
pickle_file(hopkins_pickle_file_path, hopkins_dictionary)
# pickle_file(ives_pickle_file_path, ives_dictionary)

print(len(jim_dictionary))
print(len(hopkins_dictionary))

print("finished pickle")
