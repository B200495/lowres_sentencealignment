"""
Pickles frequency list object to ensure it remains static during experimentation. Returns list of 500 most frequent terms in English for use in trainset_process.py
Modify filepaths before running.
"""
from wordfreq import top_n_list
import pickle

### FUNCTIONS ###

def pickle_file(pickle_file_path, dict_obj):
    """ Save the dictionary as a pickle object """
    with open(pickle_file_path, "wb") as file:
        pickle.dump(dict_obj, file)

### CONSTANTS ###

pickle_filepath = #ADD: e.g. "./dict_transl/top500list_en.pickle"

### CODE ###

top_500 = top_n_list("en", 500, wordlist='best')

print(top_500)

pickle_file(pickle_filepath, top_500)
