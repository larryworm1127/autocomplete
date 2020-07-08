"""Test Autocompleter classes

=== Module description ===
This module contains tests for prefix_tree.py module.
"""
import re
from typing import List

from hypothesis import given
from hypothesis.strategies import lists, from_regex

from autocomplete.prefix_tree import (
    SimplePrefixTree,
    CompressedPrefixTree,
    find_common_prefix_len
)

# Global variables
regex = re.compile('[a-zA-Z]')


# ------------------------------------------------------------------------------
# Test SimplePrefixTree insert
# ------------------------------------------------------------------------------
@given(from_regex(regex), lists(from_regex(regex), min_size=2, unique=True))
def test_spt_insert_simple(value: str, n: List[str]) -> None:
    """Test insert method in SimplePrefixTree with simple insertions.
    """
    # insert single value with empty prefix
    t1 = SimplePrefixTree('sum')
    t1.insert(value, 1.0, [])
    assert len(t1) == 1
    assert t1.weight == 1.0
    assert t1.value == []
    assert t1.subtrees[0].value == value

    # insert single value with prefix of length 1
    t2 = SimplePrefixTree('sum')
    t2.insert(value, 1.0, ['a'])
    assert len(t2) == 1
    assert t2.weight == 1.0
    assert t2.value == []
    assert t2.subtrees[0].value == ['a']
    assert t2.subtrees[0].subtrees[0].value == value

    # insert single value with prefix n of random length
    t3 = SimplePrefixTree('sum')
    t3.insert(value, 1.0, n)
    assert len(t3) == 1
    assert t3.weight == 1.0
    assert t3.value == []
    assert t3.subtrees[0].value == [n[0]]
    assert t3.subtrees[0].subtrees[0].value == [n[0], n[1]]


def test_spt_insert_sum_weight() -> None:
    """Test insert method in SimplePrefixTree with sum aggregated weight.
    """
    t = SimplePrefixTree('sum')

    # ['c'] prefix
    t.insert('cat', 2.0, ['c', 'a', 't'])
    assert t.weight == 2.0

    t.insert('cat', 2.0, ['c', 'a', 't'])
    assert t.weight == 4.0

    t.insert('care', 3.0, ['c', 'a', 'r', 'e'])
    assert t.weight == 7.0
    assert t.subtrees[0].subtrees[0].subtrees[1].weight == 3.0

    t.insert('car', 4.0, ['c', 'a', 'r'])
    assert t.weight == 11.0
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 7.0

    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    assert t.weight == 14.0
    assert t.subtrees[0].subtrees[0].subtrees[0].value == ['c', 'a', 'r']
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 7.0
    assert t.subtrees[0].subtrees[0].subtrees[1].weight == 7.0

    t.insert('cater', 1.0, ['c', 'a', 't', 'e', 'r'])
    assert t.weight == 15.0
    assert t.subtrees[0].subtrees[0].subtrees[0].value == ['c', 'a', 't']
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 8.0

    # ['d'] prefix
    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    assert t.weight == 20.0
    assert t.subtrees[1].weight == 5.0

    t.insert('danger', 20.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    assert t.weight == 40.0
    assert t.subtrees[0].value == ['d']
    assert t.subtrees[0].weight == 25.0


def test_spt_insert_avg_weight() -> None:
    """Test insert method in SimplePrefixTree with average aggregated weight.
    """
    t = SimplePrefixTree('average')

    # ['c'] prefix
    t.insert('cat', 2.0, ['c', 'a', 't'])
    assert t.weight == 2.0

    t.insert('cat', 2.0, ['c', 'a', 't'])
    assert t.weight == 4.0

    t.insert('care', 3.0, ['c', 'a', 'r', 'e'])
    assert t.weight == 3.5
    assert t.subtrees[0].subtrees[0].subtrees[1].weight == 3.0

    t.insert('car', 4.0, ['c', 'a', 'r'])
    assert t.weight == 3.6666666666666665
    assert t.subtrees[0].subtrees[0].subtrees[0].value == ['c', 'a', 't']
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 4.0

    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    assert t.weight == 3.5
    assert t.subtrees[0].subtrees[0].subtrees[0].value == ['c', 'a', 't']
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 3.5
    assert t.subtrees[0].subtrees[0].subtrees[1].weight == 3.5

    t.insert('cater', 2.0, ['c', 'a', 't', 'e', 'r'])
    assert t.weight == 3.2
    assert t.subtrees[0].subtrees[0].subtrees[0].value == ['c', 'a', 'r']
    assert t.subtrees[0].subtrees[0].subtrees[0].weight == 3.5

    # ['d'] prefix
    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    assert t.weight == 3.5
    assert t.subtrees[0].value == ['d']
    assert t.subtrees[0].weight == 5.0

    t.insert('danger', 28.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    assert t.weight == 7.0
    assert t.subtrees[0].value == ['d']
    assert t.subtrees[0].weight == 16.5


def test_spt_autocomplete() -> None:
    """Test autocomplete method in SimplePrefixTree with both weight types.
    """
    # sum weight type
    t1 = SimplePrefixTree('sum')
    t1.insert('care', 2.0, ['c', 'a', 'r', 'e'])
    t1.insert('car', 1.0, ['c', 'a', 'r'])
    t1.insert('danger', 4.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t1.insert('door', 3.0, ['d', 'o', 'o', 'r'])
    t1.insert('cat', 5.0, ['c', 'a', 't'])

    assert t1.autocomplete(['c', 'a']) == [('cat', 5.0), ('care', 2.0),
                                           ('car', 1.0)]
    assert t1.autocomplete(['c', 'a'], 2) == [('cat', 5.0), ('care', 2.0)]
    assert t1.autocomplete(['c', 'a'], 1) == [('cat', 5.0)]
    assert t1.autocomplete(['d']) == [('danger', 4.0), ('door', 3.0)]
    assert t1.autocomplete(['d'], 1) == [('danger', 4.0)]
    assert t1.autocomplete([], 1) == [('cat', 5.0)]

    # average weight type
    t2 = SimplePrefixTree('average')
    t2.insert('care', 2.0, ['c', 'a', 'r', 'e'])
    t2.insert('car', 1.0, ['c', 'a', 'r'])
    t2.insert('cent', 7.0, ['c', 'e', 'n', 't'])
    t2.insert('center', 14.0, ['c', 'e', 'n', 't', 'e', 'r'])
    t2.insert('danger', 4.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t2.insert('dan', 1.0, ['d', 'a', 'n'])
    t2.insert('door', 3.0, ['d', 'o', 'o', 'r'])
    t2.insert('cat', 5.0, ['c', 'a', 't'])

    assert t2.autocomplete(['c']) == [('center', 14.0), ('cent', 7.0),
                                      ('cat', 5.0), ('care', 2.0), ('car', 1.0)]
    assert t2.autocomplete(['c'], 2) == [('center', 14.0), ('cent', 7.0)]
    assert t2.autocomplete(['c'], 3) == [('center', 14.0), ('cent', 7.0),
                                         ('cat', 5.0)]
    assert t2.autocomplete(['d']) == [('danger', 4.0), ('door', 3.0),
                                      ('dan', 1.0)]
    assert t2.autocomplete(['d'], 1) == [('door', 3.0)]
    assert t2.autocomplete([], 1) == [('center', 14.0)]
    assert t2.autocomplete([], 2) == [('center', 14.0), ('cent', 7.0)]


def test_spt_remove_sum_weight() -> None:
    """Test remove method in SimplePrefixTree with sum weight types.
    """
    # --------------------------------------------------------------------------
    # Remove entire tree
    t1 = SimplePrefixTree('sum')
    t1.insert('cat', 1.0, ['c', 'a', 't'])
    t1.remove([])

    # tree should be empty
    assert t1.is_empty()

    # --------------------------------------------------------------------------
    # Remove branch causes removal of entire tree
    t2 = SimplePrefixTree('sum')
    t2.insert('cat', 1.0, ['c', 'a', 't'])
    t2.remove(['c', 'a'])

    # tree should be empty
    assert t2.is_empty()

    # --------------------------------------------------------------------------
    # Remove branch
    t3 = SimplePrefixTree('sum')
    t3.insert('cat', 2.0, ['c', 'a', 't'])
    t3.insert('care', 3.0, ['c', 'a', 'r', 'e'])
    t3.insert('car', 4.0, ['c', 'a', 'r'])
    t3.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t3.insert('cater', 2.0, ['c', 'a', 't', 'e', 'r'])
    t3.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t3.insert('danger', 28.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t3.remove(['c', 'a', 'r'])

    # no more ['c', 'a', 'r']
    assert t3.subtrees[1].subtrees[0].value == ['c', 'a']
    assert len(t3.subtrees[1].subtrees) == 1

    # check for weights
    assert t3.weight == 40.0
    assert t3.subtrees[1].weight == 7.0


def test_spt_remove_avg_weight() -> None:
    """Test remove method in SimplePrefixTree with average weight types.
    """
    t = SimplePrefixTree('average')
    t.insert('cat', 4.0, ['c', 'a', 't'])
    t.insert('care', 3.0, ['c', 'a', 'r', 'e'])
    t.insert('car', 4.0, ['c', 'a', 'r'])
    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t.insert('cater', 2.0, ['c', 'a', 't', 'e', 'r'])
    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t.insert('danger', 28.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t.remove(['c', 'a', 'r'])

    # no more ['c', 'a', 'r']
    assert t.subtrees[1].subtrees[0].value == ['c', 'a']
    assert len(t.subtrees[1].subtrees) == 1

    # check for weights
    assert t.weight == 8.4
    assert t.subtrees[1].weight == 3.0


# ------------------------------------------------------------------------------
# Test CompressedPrefixTree
# ------------------------------------------------------------------------------
@given(from_regex(regex), lists(from_regex(regex), min_size=2, unique=True))
def test_cpt_insert_simple(value: str, n: List[str]) -> None:
    """Test insert method in CompressedPrefixTree with simple insertions.
    """
    # insert single value with empty prefix
    t1 = CompressedPrefixTree('sum')
    t1.insert(value, 1.0, [])
    assert len(t1) == 1
    assert t1.weight == 1.0
    assert t1.value == []
    assert t1.subtrees[0].value == value

    # insert single value with prefix of length 1
    t2 = CompressedPrefixTree('sum')
    t2.insert(value, 1.0, ['a'])
    assert len(t2) == 1
    assert t2.weight == 1.0
    assert t2.value == ['a']
    assert t2.subtrees[0].value == value

    # insert single value with prefix n of random length
    t3 = CompressedPrefixTree('sum')
    t3.insert(value, 1.0, n)
    assert len(t3) == 1
    assert t3.weight == 1.0
    assert t3.value == n
    assert t3.subtrees[0].value == value


def test_cpt_insert_sum_weight() -> None:
    """Test insert method in CompressedPrefixTree with sum aggregated weight.
    """
    t = CompressedPrefixTree('sum')
    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t.insert('car', 4.0, ['c', 'a', 'r'])
    t.insert('car', 1.0, ['c', 'a', 'r'])
    assert t.value == ['c', 'a']
    assert len(t.subtrees) == 2
    assert t.weight == 8.0

    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('cater', 6.0, ['c', 'a', 't', 'e', 'r'])
    assert t.subtrees[0].value == ['c', 'a', 't']
    assert len(t.subtrees[0].subtrees[0].subtrees) == 2
    assert t.weight == 16.0

    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t.insert('danger', 9.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t.insert('dan', 5.0, ['d', 'a', 'n'])
    assert t.subtrees[0].value == ['d']
    assert len(t.subtrees[0].subtrees) == 2
    assert t.weight == 35.0


def test_cpt_insert_avg_weight() -> None:
    """Test insert method in CompressedPrefixTree with average weight.
    """
    t = CompressedPrefixTree('average')
    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t.insert('car', 4.0, ['c', 'a', 'r'])
    assert t.value == ['c', 'a']
    assert len(t.subtrees) == 2
    assert t.weight == 3.5

    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('cater', 6.0, ['c', 'a', 't', 'e', 'r'])
    assert t.subtrees[0].value == ['c', 'a', 'r']
    assert len(t.subtrees[0].subtrees) == 1
    assert t.weight == 3.75

    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t.insert('danger', 9.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t.insert('dan', 5.0, ['d', 'a', 'n'])
    assert t.subtrees[0].value == ['d']
    assert len(t.subtrees[0].subtrees) == 2
    assert t.weight == 4.857142857142857


def test_cpt_autocomplete() -> None:
    t = CompressedPrefixTree('sum')
    t.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t.insert('car', 4.0, ['c', 'a', 'r'])
    t.insert('car', 4.0, ['c', 'a', 'r'])
    t.insert('cat', 2.0, ['c', 'a', 't'])
    t.insert('cater', 6.0, ['c', 'a', 't', 'e', 'r'])
    t.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t.insert('danger', 9.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t.insert('dan', 5.0, ['d', 'a', 'n'])

    result = t.autocomplete([], 3)
    assert result[0] == ('cater', 6.0)
    assert result[1] == ('cate', 3.0)
    assert result[2] == ('cat', 2.0)


def test_cpt_insert_same_prefix() -> None:
    t1 = CompressedPrefixTree('sum')
    t1.insert('about', 1.0, ['a', 'b', 'o', 'u', 't'])
    t1.insert('an', 1.0, ['a', 'n'])
    t1.insert('all', 1.0, ['a', 'l', 'l'])
    t1.insert('as', 1.0, ['a', 's'])
    t1.insert('at', 1.0, ['a', 't'])
    t1.insert('are', 1.0, ['a', 'r', 'e'])
    t1.insert('and', 1.0, ['a', 'n', 'd'])
    t1.insert('a', 1.0, ['a'])

    assert len(t1.subtrees) == 7
    assert t1.value == ['a']


def test_cpt_remove_sum_weight() -> None:
    """Test remove method in CompressedPrefixTree with sum weight types.
    """
    t2 = CompressedPrefixTree('sum')
    t2.insert('cate', 3.0, ['c', 'a', 't', 'e'])
    t2.insert('car', 4.0, ['c', 'a', 'r'])
    t2.insert('car', 4.0, ['c', 'a', 'r'])
    t2.insert('cat', 2.0, ['c', 'a', 't'])
    t2.insert('cater', 6.0, ['c', 'a', 't', 'e', 'r'])
    t2.insert('door', 5.0, ['d', 'o', 'o', 'r'])
    t2.insert('danger', 9.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t2.insert('dan', 5.0, ['d', 'a', 'n'])
    t2.insert('kaput', 9.0, ['k', 'a', 'p', 'u', 't'])
    t2.insert('karat', 7.0, ['k', 'a', 'r', 'a', 't'])

    t2.remove(['c'])
    assert len(t2.subtrees) == 2

    t2.remove(['k'])
    assert t2.value == ['d']

    t2.remove(['d'])
    assert t2.is_empty()


def test_cpt_complex() -> None:
    """Test various things for a complex CompressedPrefixTree.
    """
    t1 = CompressedPrefixTree('sum')
    t1.insert('care', 2.0, ['c', 'a', 'r', 'e'])
    t1.insert('car', 1.0, ['c', 'a', 'r'])
    t1.insert('car', 1.0, ['c', 'a', 'r'])
    t1.insert('cart', 1.0, ['c', 'a', 'r', 't'])
    t1.insert('danger', 4.0, ['d', 'a', 'n', 'g', 'e', 'r'])
    t1.insert('door', 3.0, ['d', 'o', 'o', 'r'])
    t1.insert('cat', 5.0, ['c', 'a', 't'])
    t1.insert('dog', 2.0, ['c', 'a', 't'])

    assert len(t1) == 7
    assert t1.value == []
    assert t1.subtrees[0].value == ['c', 'a']
    assert t1.subtrees[1].value == ['d']


def test_find_common_prefix_len() -> None:
    """Test <find_common_prefix_len> function.
    """
    assert find_common_prefix_len(['c', 'a', 't'], ['c', 'a', 'r']) == 2
    assert find_common_prefix_len(['c', 'a', 't', 'e'], ['c', 'a', 't']) == 3
    assert find_common_prefix_len(['c', 'a', 't'], ['c', 'a', 't', 'e']) == 3


if __name__ == '__main__':
    import pytest

    pytest.main(['test_prefix_tree.py'])
