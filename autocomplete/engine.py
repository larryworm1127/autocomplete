"""Autocomplete engines

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.
"""
from __future__ import annotations

import csv
from typing import Any, Dict, List, Optional, Tuple

from .melody import Melody
from .prefix_tree import SimplePrefixTree, CompressedPrefixTree, Autocompleter


################################################################################
# Text-based Autocomplete Engines
################################################################################
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.
        """
        with open(config['file'], encoding='utf8') as f:
            if config['autocompleter'] == 'simple':
                self.autocompleter = SimplePrefixTree(config['weight_type'])
            else:
                self.autocompleter = CompressedPrefixTree(config['weight_type'])

            for line in f:
                # sanitize the line
                prefix = [char for char in line.lower().strip('\n')
                          if char.isalnum() or char == ' ']
                new_line = ''.join(prefix)

                # no alphanumeric character in line, skip to next line
                if not prefix:
                    continue

                self.autocompleter.insert(new_line, 1.0, prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix_seq = [char for char in prefix]
        return self.autocompleter.autocomplete(prefix_seq, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix_seq = [char for char in prefix]
        self.autocompleter.remove(prefix_seq)


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string
        """
        with open(config['file'], encoding='utf8') as csvfile:
            if config['autocompleter'] == 'simple':
                self.autocompleter = SimplePrefixTree(config['weight_type'])
            else:
                self.autocompleter = CompressedPrefixTree(config['weight_type'])

            reader = csv.reader(csvfile)
            for line, weight in reader:
                # sanitize the line
                words = line.lower().strip('\n').split()
                prefix = []
                for item in words:
                    chars = [char for char in item if char.isalnum()]
                    prefix.append(''.join(chars))
                new_line = ' '.join(prefix)

                # make sure prefix doesn't contain any empty strings
                fixed_prefix = [word for word in prefix if word.isalnum()]

                # no words in line, skip to next line
                if not fixed_prefix:
                    continue

                self.autocompleter.insert(new_line, float(weight), fixed_prefix)

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix_seq = prefix.split()
        return self.autocompleter.autocomplete(prefix_seq, limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix_seq = prefix.split()
        self.autocompleter.remove(prefix_seq)


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """
        with open(config['file'], encoding='utf8') as csvfile:
            if config['autocompleter'] == 'simple':
                self.autocompleter = SimplePrefixTree(config['weight_type'])
            else:
                self.autocompleter = CompressedPrefixTree(config['weight_type'])

            reader = csv.reader(csvfile)
            for line in reader:
                # separate name from notes
                name = line[0]
                notes = line[1:]

                # process notes in form of (pitch, duration)
                notes_lst = []
                for index in range(0, len(notes), 2):
                    note = notes[index]
                    duration = notes[index + 1]
                    if not (note == '' or duration == ''):
                        notes_lst.append((int(note), int(duration)))

                # insert value into auto completer
                value = Melody(name, notes_lst)
                prefix = [notes_lst[i + 1][0] - notes_lst[i][0]
                          for i in range(len(notes_lst) - 1)]
                self.autocompleter.insert(value, 1.0, prefix)

    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        value = self.autocompleter.autocomplete(prefix, limit)
        return [(melody, weight) for melody, weight in value]

    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """
        self.autocompleter.remove(prefix)


###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        'file': 'data/lotr.txt',
        # 'file': 'data/google_no_swears.txt',
        'autocompleter': 'simple',
        'weight_type': 'average'
    })
    return engine.autocomplete('frodo d', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    return engine.autocomplete('how to', 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        'file': 'data/songbook.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    melodies = engine.autocomplete([12], 20)
    for melody, _ in melodies:
        melody.play()


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(5000)

    print(sample_letter_autocomplete())
