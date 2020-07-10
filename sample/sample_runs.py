"""Sample Runs

=== Module description ===
This file contains 3 sample runs for the autocomplete engine. The data for the
sample runs are in data folder.
"""
from dataclasses import dataclass
from typing import List, Tuple

import fire

from autocomplete.engine import (
    LetterAutocompleteEngine,
    SentenceAutocompleteEngine,
    MelodyAutocompleteEngine
)


@dataclass
class Samples:
    """Class containing all sample runs for autocomplete engine.
    """
    autocompleter: str = 'compressed'
    weight_type: str = 'sum'

    def letter_autocomplete(self) -> List[Tuple[str, float]]:
        """A sample run of the letter autocomplete engine.
        """
        engine = LetterAutocompleteEngine({
            'file': 'data/lotr.txt',
            'autocompleter': self.autocompleter,
            'weight_type': self.weight_type
        })
        return engine.autocomplete('frodo d', 20)

    def sentence_autocomplete(self) -> List[Tuple[str, float]]:
        """A sample run of the sentence autocomplete engine.
        """
        engine = SentenceAutocompleteEngine({
            'file': 'data/google_searches.csv',
            'autocompleter': self.autocompleter,
            'weight_type': self.weight_type
        })
        return engine.autocomplete('how to', 20)

    def melody_autocomplete(self) -> None:
        """A sample run of the melody autocomplete engine.

        Note that sample melody plays the autocomplete melodies in sequence.
        Make sure you have sound on to listen to the melodies!
        """
        engine = MelodyAutocompleteEngine({
            'file': 'data/songbook.csv',
            'autocompleter': self.autocompleter,
            'weight_type': self.weight_type
        })
        melodies = engine.autocomplete([12], 20)
        for melody, _ in melodies:
            melody.play()


if __name__ == '__main__':
    import sys

    sys.setrecursionlimit(5000)
    fire.Fire(Samples)
