"""Autocompleter classes

This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
"""
from __future__ import annotations

from typing import Any, List, Optional, Tuple, Union, Dict


class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]

    # === Private Attributes ===
    # Specifies how the aggregate weight of non-leaf trees should be calculated
    _weight_type: str
    # The number of values stored in the tree
    _length: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated.
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self._weight_type = weight_type
        self._length = 0

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        return self._length

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        # check whether prefix is empty or not
        if prefix:
            subtree = self.get_matching_subtree(prefix)

            # found subtree that matches given prefix
            if subtree is not None:
                subtree.insert(value, weight, prefix)
                self.subtrees.sort(key=lambda s: s.weight, reverse=True)
                self._length = sum([len(s) for s in self.subtrees])
                self.weight = self.get_aggr_weight()

            # prefix matches exactly with subtree value
            elif self.value == prefix:
                # check if the value is already inserted
                sub = self.get_matching_subtree(value)
                if sub is not None:
                    sub.weight += weight
                    self.weight = self.get_aggr_weight()
                else:
                    self.insert_spt(value, weight, prefix, len(prefix))

            # no subtree matches, create a brand new subtree
            else:
                self.insert_spt(value, weight, prefix, len(self.value))
        else:
            self.insert_spt(value, weight, prefix, len(prefix))

    def insert_spt(self, value: Any, weight: float, prefix: List,
                   depth: int) -> None:
        """Inserting a new SimplePrefixTree into subtrees list.

        === Attributes ===
        value:
            The string value to be inserted.
        weight:
            The weight of the string value.
        prefix:
            The prefix sequence of the string value.
        depth:
            The current prefix sequence depth of the tree.
        """
        # create new subtree
        subtree = SimplePrefixTree(self._weight_type)
        self.value = prefix[:depth]

        # check to whether continue recur downward or insert value directly
        if depth < len(prefix):
            subtree.insert_spt(value, weight, prefix, depth + 1)
        else:
            subtree.value = value
            subtree.weight += weight
            subtree._length += 1

        # update size, subtree list and weight
        self._length += 1
        self.subtrees.append(subtree)
        self.subtrees.sort(key=lambda s: s.weight, reverse=True)
        self.weight = self.get_aggr_weight()

    def get_aggr_weight(self) -> float:
        """Return the aggregated weight of the current tree.
        """
        # sum aggregated weight
        if self._weight_type == 'sum':
            weight = sum([sub.weight for sub in self.subtrees])
        # average aggregated weight
        else:
            if len(self.subtrees) == 0:
                weight = self.weight
            elif len(self.subtrees) == 1:
                weight = self.subtrees[0].weight
            else:
                sub_weight = self.get_total_leaf_weights()
                weight = sub_weight / len(self)

        return weight

    def get_total_leaf_weights(self) -> float:
        """Return the total weights of the leaves of the tree.
        """
        weight = 0
        for subtree in self.subtrees:
            if subtree.is_leaf():
                weight += subtree.weight
            else:
                weight += subtree.weight * len(subtree)

        return weight

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight.

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        result = []

        # tree is empty
        if self.is_empty():
            return result

        # prefix matches subtree value
        elif prefix in (self.value, self.value[:len(prefix)]):
            new_limit = limit if limit else float('inf')
            self.autocomplete_helper(new_limit, result)
            return sorted(result, key=lambda s: s[1], reverse=True)

        # finding subtree that match the prefix
        else:
            # find the subtree that contains given prefix
            subtree = self.get_matching_subtree(prefix)
            if subtree is not None:
                result.extend(subtree.autocomplete(prefix, limit))

            # no match found
            return result

    def autocomplete_helper(self, limit: int, result: List) -> None:
        """Find all values stored under current tree and add them to given
        result list.

        === Attributes ===
        limit:
            The limit for the number of autocomplete result.
        result:
            The result list to put all the values found in.
        """
        items = []
        for subtree in self.subtrees:
            # reaches limit - immediately returns
            if len(items) == limit:
                break

            # subtree value is prefix sequence
            if not subtree.is_leaf():
                new_limit = limit - len(items)
                subtree.autocomplete_helper(new_limit, items)
            # subtree value is actual word
            else:
                items.append((subtree.value, subtree.weight))

        result.extend(items)

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        # tree is empty
        if self.is_empty():
            return

        # prefix equal to subtree value
        elif prefix == self.value:
            self.subtrees = []
            self.weight = 0.0
            self.value = []
            self._length -= 1

        # look for subtree with matching value
        else:
            # find subtree and recur call into that subtree
            subtree = self.get_matching_subtree(prefix)
            if subtree is not None:
                subtree.remove(prefix)

                # only remove subtree if it is a empty subtree
                if subtree.is_empty():
                    self.subtrees.remove(subtree)

                # update weight
                self._length = sum([len(sub) for sub in self.subtrees])
                self.weight = self.get_aggr_weight()

    def get_matching_subtree(self, prefix: Union[List, str],
                             both_way: bool = False) -> Optional[Any]:
        """Return the subtree that partially/fully matches with given prefix.

        === Attributes ===
        prefix:
            The given prefix sequence or value to match with subtree values.
        both_way:
            The condition variable to also check whether value contains prefix.
        """
        for subtree in self.subtrees:
            # check if subtree.value is part of prefix
            if prefix[:len(subtree.value)] == subtree.value:
                return subtree

            # check if prefix is part of subtree.value
            elif both_way and subtree.value[:len(prefix)] == prefix:
                return subtree

        # no subtree found
        return None


################################################################################
# CompressedPrefixTree
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - This tree does not contain any compressible internal values.

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    _length: int
    _weight_type: str

    def find_max_common_subtree(self, prefix: List
                                ) -> Tuple[List, CompressedPrefixTree]:
        """Returns the subtree with common prefix as the given prefix sequence.
        """
        result = ([], None)
        prefix_subtrees = [tree for tree in self.subtrees
                           if isinstance(tree.value, list)]

        for item in prefix_subtrees:
            common_len = find_common_prefix_len(prefix, item.value)
            if len(result[0]) < common_len:
                result = prefix[:common_len], item

        return result

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        # tree is empty
        if self.is_empty():
            self.value = prefix
            self.weight = weight
            subtree = self.create_subtree(value, weight)
            self.subtrees.append(subtree)
            self._length += 1
            return

        # if self.value has values in it
        elif self.value:
            clone_tree = self.create_subtree(self.value, self.weight,
                                             self.subtrees, self._length)
            subtree = self.create_subtree([], self.weight, [clone_tree],
                                          self._length)
            subtree.insert_cpt(value, weight, prefix)
            if len(subtree.subtrees) > 1:
                self.value = []
                self.subtrees = subtree.subtrees
                self._length = subtree._length
            else:
                self.value = subtree.subtrees[0].value
                self.subtrees = subtree.subtrees[0].subtrees
                self._length = subtree.subtrees[0]._length

            self.weight = self.get_aggr_weight()
        else:
            self.insert_cpt(value, weight, prefix)

    def insert_cpt(self, value: Any, weight: float, prefix: List) -> None:
        """Inserting a new ComplexPrefixTree into subtrees list.

        === Attributes ===
        value:
            The string value to be inserted.
        weight:
            The weight of the string value.
        prefix:
            The prefix sequence of the string value.
        """
        common, found = self.find_max_common_subtree(prefix)
        # find more than parent node
        if found is not None and self.value != common:
            data = {"prefix": prefix, "value": value, "weight": weight}
            node = self.merge_value(found, common, data)
            # If found and node is the same, we don't need to remove, append
            # same address in memory
            if found != node:
                self.subtrees.remove(found)
                self.subtrees.append(node)

        else:
            node = CompressedPrefixTree(self._weight_type)
            node.insert(value, weight, prefix)
            self.subtrees.append(node)

        # update weight and sort subtree by weight
        self._length += 1
        self.weight = self.get_aggr_weight()
        self.subtrees.sort(key=lambda s: s.weight, reverse=True)

    def merge_value(self, found: CompressedPrefixTree, common: List,
                    data: Dict[str, Union[List, str, float]]
                    ) -> CompressedPrefixTree:
        """Return a subtree that contains common prefix tree and current tree.

        === Attributes ===
        found:
            The subtree with common prefix.
        prefix:
            The prefix sequence of the value to be inserted.
        value:
            The value to be inserted.
        weight:
            The weight of the value.
        common:
            The common prefix between <found> value and given prefix.
        """
        prefix = data['prefix']
        value = data['value']
        weight = data['weight']

        # common prefix tree have same value as given prefix
        if found.value == prefix:
            if found.subtrees[0].value == value:
                found.subtrees[0].weight += weight
            else:
                new_tree = self.create_subtree(value, weight)
                found.subtrees.append(new_tree)
                found._length += 1

            found.weight = found.get_aggr_weight()
            return found

        # common prefix tree value contains given prefix
        elif found.value[:len(prefix)] == prefix:
            new_tree = self.create_subtree(value, weight)
            subtree = self.create_subtree(common, 0.0, [new_tree, found],
                                          found._length + new_tree._length)
            return subtree

        # given prefix contains common prefix tree value
        elif prefix[:len(found.value)] == found.value:
            found.insert_cpt(value, weight, prefix)
            return found

        # common prefix tree value have some common prefix with given prefix
        else:
            # common prefix
            new_tree_sub = self.create_subtree(value, weight)
            new_tree = self.create_subtree(prefix, weight, [new_tree_sub])
            subtree = self.create_subtree(common, 0.0, [new_tree, found],
                                          found._length + new_tree._length)
            return subtree

    def create_subtree(self, value: Union[List, str], weight: float,
                       subtrees: Optional[List] = None,
                       length: int = 1) -> CompressedPrefixTree:
        """Return a CompressedPrefixTree created with given properties.

        === Attributes ===
        value:
            The value of the new tree.
        weight:
            The weight of the new tree.
        length:
            The length of the tree
        """
        subtrees = list() if subtrees is None else subtrees

        # initialize tree
        tree = CompressedPrefixTree(self._weight_type)
        tree.value = value
        tree.subtrees = subtrees
        tree._length = length
        tree.weight = weight if weight != 0.0 else tree.get_aggr_weight()

        return tree

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        result = []

        # tree is empty
        if self.is_empty():
            return result

        # prefix matches subtree value
        elif prefix in (self.value, self.value[:len(prefix)]):
            new_limit = limit if limit else float('inf')
            self.autocomplete_helper(new_limit, result)
            return sorted(result, key=lambda s: s[1], reverse=True)

        # finding subtree that match the prefix
        else:
            # find the subtree that contains given prefix
            subtree = self.get_matching_subtree(prefix, both_way=True)
            if subtree is not None:
                result.extend(subtree.autocomplete(prefix, limit))

            # no match found
            return result

    def autocomplete_helper(self, limit: int, result: List) -> None:
        """Find all values stored under current tree.

        === Attributes ===
        limit:
            The limit for the number of autocomplete result.
        result:
            The result list to put all the values found in.
        """
        items = []
        for subtree in self.subtrees:
            # reaches limit - immediately returns
            if len(items) == limit:
                break

            # subtree value is prefix sequence
            if not subtree.is_leaf():
                new_limit = limit - len(items)
                subtree.autocomplete_helper(new_limit, items)
            # subtree value is actual word
            else:
                items.append((subtree.value, subtree.weight))

        result.extend(items)

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        # tree is empty
        if self.is_empty():
            return

        # prefix equal to subtree value or subtree value contains prefix
        elif prefix in (self.value, self.value[:len(prefix)]):
            self.subtrees = []
            self.weight = 0.0
            self.value = []
            self._length -= 1

        # look for subtree with matching value
        else:
            # find subtree and recur call into that subtree
            subtree = self.get_matching_subtree(prefix, both_way=True)
            if subtree is not None:
                subtree.remove(prefix)

                # only remove subtree if it is a empty subtree
                if subtree.is_empty():
                    self.subtrees.remove(subtree)

                # compress subtree
                if len(self.subtrees) == 1:
                    only_sub = self.subtrees[0]
                    self.value = only_sub.value
                    self.weight = only_sub.weight
                    self.subtrees.extend(only_sub.subtrees)
                    self.subtrees.remove(only_sub)

                # update weight
                self.weight = self.get_aggr_weight()


def find_common_prefix_len(prefix1: List, prefix2: List) -> int:
    """Returns common prefix size of the given two prefix sequences.
    """
    result = 0
    for index in range(min(len(prefix1), len(prefix2))):
        if prefix1[index] == prefix2[index]:
            result = index + 1
        else:
            break

    return result
