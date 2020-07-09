************
Autocomplete
************

Description
###########
The autocomplete is a simple Python library that contains autocomplete
engines for letters, sentences, as well as melodies given the prefix
of the content. The engine takes either a text file (each sentence
on a single line) or a CSV file, and converts the content of the file
into a weighted tree data structure in which it then searches through
the tree for the given prefix.

The autocomplete engine is a modified version of a project done at
U of T.

**Note:** melody autocomplete requires MIDI data file. See sample data
file to learn more.


Installation
############

So far the library can't be embedded directly, so to use it, clone
the repo and install the dependencies by running
:code:`pip install -r requirement.txt`


Usage
#####
A autocomplete data file is required for the engine to work at all.
Once the data file is present, you can choose what type of autocomplete
you want (letter, sentence, melody).

Here's an example of calling letter autocomplete engine.

.. code-block:: python

    from autocomplete import LetterAutocompleteEngine

    # All autocomplete engines takes a config dict
    engine = LetterAutocompleteEngine({
        'file': 'path/file.txt',    # or file.csv
        'autocompleter': 'simple',  # or 'complex'
        'weight_type': 'sum'        # or 'average'
    })
    print(engine.autocomplete(
        'prefix you want to autocomplete',
        20   # number of results
    ))

See documentation for config dictionary format.

The sample folder contains some sample usage of each autocomplete
engine. The file can be ran in command line to produce autocomplete
results from sample data.

**Note:** 
..code:`LetterAutocompleteEngine` 
will take some time to 
run due to the size of the sample data. (over 34000 lines of sentences
to autocomplete from)

