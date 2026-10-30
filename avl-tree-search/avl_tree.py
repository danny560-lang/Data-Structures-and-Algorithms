"""
avl_tree.py
Module Four Assignment - Part 1: AVL Tree

A self-balancing binary search tree (AVL tree) written from scratch, without
any library data structures. Each node stores one distinct word plus a count
of how many times that word was inserted, so duplicate words in the data set
are kept without adding extra nodes.

Features:
    - insert()            recursive insertion that rebalances on the way back up
    - _rebalance()        detects the four imbalance cases (LL, RR, LR, RL)
    - rotate_left/right   the single rotations used to restore balance
    - search()            binary search over the tree (Part 2, see avl_search.py)
    - traversals          in-order, pre-order, post-order, and level-order
    - validate()          checks the BST ordering, stored heights, and balance
"""


class AVLNode:
    """A single node in the AVL tree."""

    def __init__(self, word):
        self.word = word      # the key used for ordering
        self.count = 1        # number of times this word appeared in the data
        self.height = 1       # a new node is a leaf, so its height is 1
        self.left = None
        self.right = None


class AVLTree:
    """An AVL tree that keeps itself balanced after every insertion."""

    def __init__(self):
        self.root = None
        self.size = 0              # number of distinct words (nodes)
        self.total_inserted = 0    # number of words inserted, duplicates included
        self.rotations = 0         # how many rotations were needed while loading

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @staticmethod
    def _height(node):
        """Height of a subtree; an empty subtree has height 0."""
        return node.height if node is not None else 0

    def _update_height(self, node):
        """Recalculate a node's height from its children."""
        left_height = self._height(node.left)
        right_height = self._height(node.right)
        node.height = 1 + (left_height if left_height > right_height else right_height)

    def _balance_factor(self, node):
        """Left height minus right height. AVL requires -1, 0, or 1."""
        if node is None:
            return 0
        return self._height(node.left) - self._height(node.right)

    def height(self):
        """Height of the whole tree."""
        return self._height(self.root)

    # ------------------------------------------------------------------
    # Rotations (balancing)
    # ------------------------------------------------------------------
    def rotate_right(self, y):
        """
        Right rotation around y. Used when the left side is too tall.
        
        """
        x = y.left
        moved_subtree = x.right

        x.right = y
        y.left = moved_subtree

        self._update_height(y)   # y is now lower, so update it first
        self._update_height(x)
        self.rotations += 1
        return x                 # x is the new root of this subtree

    def rotate_left(self, x):
        """
        Left rotation around x. Used when the right side is too tall.

        """
        y = x.right
        moved_subtree = y.left

        y.left = x
        x.right = moved_subtree

        self._update_height(x)
        self._update_height(y)
        self.rotations += 1
        return y

    def _rebalance(self, node):
        """
        Restore the AVL property at this node if it is out of balance and
        return the (possibly new) root of the subtree.
        """
        self._update_height(node)
        balance = self._balance_factor(node)

        # Left side too tall
        if balance > 1:
            if self._balance_factor(node.left) < 0:
                # Left-Right case: rotate the left child left first
                node.left = self.rotate_left(node.left)
            # Left-Left case (or the second half of Left-Right)
            return self.rotate_right(node)

        # Right side too tall
        if balance < -1:
            if self._balance_factor(node.right) > 0:
                # Right-Left case: rotate the right child right first
                node.right = self.rotate_right(node.right)
            # Right-Right case (or the second half of Right-Left)
            return self.rotate_left(node)

        return node  # already balanced

    # ------------------------------------------------------------------
    # Insertion
    # ------------------------------------------------------------------
    def insert(self, word):
        """Insert a word into the tree, rebalancing as needed."""
        self.root = self._insert(self.root, word)
        self.total_inserted += 1

    def _insert(self, node, word):
        # Standard binary search tree insertion
        if node is None:
            self.size += 1
            return AVLNode(word)

        if word < node.word:
            node.left = self._insert(node.left, word)
        elif word > node.word:
            node.right = self._insert(node.right, word)
        else:
            # Duplicate word: count it instead of adding a second node
            node.count += 1
            return node

        # On the way back up, fix any imbalance this insertion caused
        return self._rebalance(node)

    # ------------------------------------------------------------------
    # Search (used by Part 2)
    # ------------------------------------------------------------------
    def search(self, word):
        """
        Binary search through the AVL tree.

        Starting at the root, compare the target with the current node's word
        and move left if it is smaller or right if it is larger, discarding
        half of the remaining tree at every step.

        Returns a tuple (node, path):
            node  - the matching AVLNode, or None if the word is not in the tree
            path  - the list of words of every node accessed during the search
        """
        path = []
        current = self.root
        while current is not None:
            path.append(current.word)
            if word == current.word:
                return current, path
            if word < current.word:
                current = current.left
            else:
                current = current.right
        return None, path

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------
    def inorder(self):
        """Left, node, right. Returns the words in sorted order."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is not None:
            self._inorder(node.left, result)
            result.append(node.word)
            self._inorder(node.right, result)

    def preorder(self):
        """Node, left, right."""
        result = []
        self._preorder(self.root, result)
        return result

    def _preorder(self, node, result):
        if node is not None:
            result.append(node.word)
            self._preorder(node.left, result)
            self._preorder(node.right, result)

    def postorder(self):
        """Left, right, node."""
        result = []
        self._postorder(self.root, result)
        return result

    def _postorder(self, node, result):
        if node is not None:
            self._postorder(node.left, result)
            self._postorder(node.right, result)
            result.append(node.word)

    def level_order(self, max_levels=None):
        """
        Breadth-first traversal. Returns a list of levels, where each level
        is a list of words. A plain list with a moving index is used as the
        queue so no library queue is needed.
        """
        if self.root is None:
            return []
        levels = []
        current_level = [self.root]
        while current_level:
            if max_levels is not None and len(levels) == max_levels:
                break
            levels.append([node.word for node in current_level])
            next_level = []
            for node in current_level:
                if node.left is not None:
                    next_level.append(node.left)
                if node.right is not None:
                    next_level.append(node.right)
            current_level = next_level
        return levels

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate(self):
        """
        Check every node for:
            - correct binary search tree ordering
            - a correctly stored height
            - a balance factor of -1, 0, or 1
        Returns True if the whole tree is a valid AVL tree.
        """
        valid, _ = self._validate(self.root, None, None)
        return valid

    def _validate(self, node, low, high):
        if node is None:
            return True, 0
        if (low is not None and node.word <= low) or (high is not None and node.word >= high):
            return False, 0
        left_ok, left_height = self._validate(node.left, low, node.word)
        right_ok, right_height = self._validate(node.right, node.word, high)
        height = 1 + (left_height if left_height > right_height else right_height)
        balanced = -1 <= left_height - right_height <= 1
        return (left_ok and right_ok and balanced and height == node.height), height
