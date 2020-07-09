"""Test Autocomplete Engine classes

=== Module description ===
This module contains tests for engine.py module.
"""
from autocomplete.engine import (
    LetterAutocompleteEngine,
    SentenceAutocompleteEngine,
    MelodyAutocompleteEngine
)


def test_letter_autocomplete() -> None:
    engine = LetterAutocompleteEngine({
        'file': 'tests/data/test_data.txt',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })

    result = engine.autocomplete('an')
    assert len(result) == 2
    assert result[0][0] == 'an'
    assert result[1][0] == 'and'

    result = engine.autocomplete('', 2)
    assert len(result) == 2
    assert result[0][0] == 'an'
    assert result[1][0] == 'and'

    result = engine.autocomplete('m')
    assert len(result) == 2
    assert result[0][0] == 'm'
    assert result[1][0] == 'many'


def test_sentence_autocomplete() -> None:
    engine = SentenceAutocompleteEngine({
        'file': 'tests/data/test_data.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })

    result = engine.autocomplete('the')
    assert len(result) == 1
    assert result[0][0] == 'the animal'
    assert result[0][1] == 150.0


def test_melody_autocomplete() -> None:
    engine = MelodyAutocompleteEngine({
        'file': 'tests/data/test_melody.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })

    result = engine.autocomplete([0])
    assert len(result) == 2
    assert result[0][0].name == 'Random melody 0'
    assert result[1][0].name == 'Random melody 2'


if __name__ == '__main__':
    import pytest

    pytest.main(["test_autocomplete_engines.py"])
