"""Sample Runs

=== Module description ===
This file contains 3 sample runs for the autocomplete engine. The data for the
sample runs are in data folder.
"""
from typing import List, Tuple

from autocomplete.engine import (
    LetterAutocompleteEngine,
    SentenceAutocompleteEngine,
    MelodyAutocompleteEngine
)


def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine.
    """
    engine = LetterAutocompleteEngine({
        'file': 'data/lotr.txt',
        'autocompleter': 'simple',
        'weight_type': 'average'
    })
    return engine.autocomplete('frodo d', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine.
    """
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'compressed',
        'weight_type': 'sum'
    })
    return engine.autocomplete('how to', 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine.

    Note that sample melody plays the autocomplete melodies in sequence.
    Make sure you have sound on to listen to the melodies!
    """
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

    # print(sample_letter_autocomplete())
    # print(sample_sentence_autocomplete())
    # print(sample_melody_autocomplete())
