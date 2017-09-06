class Tree(object):
    """
    Represents a word (tree node) in the natural language syntax tree.
    Each tree node may contain zero or more children (dependent) tree nodes.
    This representation is not tied to any specific parser implementation.
    """

    def __init__(self):
        # index of this node, if given a list of nodes
        self.index = None

        # dependency label for this word
        self.label = None

        # content (word, text)
        self.content = None

        # root word for the current word, if available
        self.lemma = None

        # the Part Of Speech tag representing the current word
        self.pos_tag = None

        # list of children (dependent) tree nodes
        self.children = []

        # mappings
        self.pos_tag_mapping = None
        self.label_mapping = None

    def walk(self):
        """
        Iterator which yields all children in the current tree. Order is not
        guaranteed to be the same as any originally provided list, but it
        _will_ remain the same over multiple calls.
        :return: all tree nodes in current tree
        :rtype list of Tree
        """
        yield self
        for child in self.children:
            for node in child.walk():
                yield node

    def filtered_walk(self, filter_func):
        """
        Iterator which yields all children in the current tree that pass the
        `filter_func` filter.

        :param filter_func this is the filter function that defines the logic
                to filter nodes so only specific nodes are yielded. This is of
                the format `def filter_func(root, current_node) -> bool:` where
                root is the tree node on which walk is called, and current_node
                is the node being tested for filtration

        :return: all tree nodes in current tree that pass the filter
        :rtype list of Tree
        """
        for node in self.walk():
            if filter_func(self, node):
                yield node

    def __repr__(self):
        return self.get_string_repr(verbose=True)

    def get_string_repr(self, verbose=True):
        """
        Get string representation for the current tree node (non recursive), depending
        on the `verbose` flag.

        :param verbose: Returns a more detailed string if this is True
        :return: Returns a string representation for the current tree node
        :rtype str
        """
        pos_tag = self.pos_tag_mapping[self.pos_tag] if self.pos_tag_mapping else self.pos_tag
        label = self.label_mapping[self.label] if self.label_mapping else self.label

        if verbose:
            return "Tree(index={},label='{}', content='{}', lemma='{}', pos_tag='{}', children=[{}])".format(
                self.index, label, self.content, self.lemma, pos_tag,
                ','.join([str(t.index) for t in self.children]))

        return "{} (pos_tag={}, label={})".format(self.content, pos_tag, label)

    def get_printable_tree(self, max_depth=None, verbose=True):
        """
        Get a string tree representation for the current tree.

        :param max_depth: The maximum depth to generate the tree. No maximum if None (default)
        :type max_depth int|None

        :param verbose: Returns a more detailed string for each node if this is True
        :type verbose bool

        :return: Returns a string tree representation for the current tree.
        :rtype str
        """
        return '\n'.join(self._get_tree_statements(max_depth, 1, verbose))

    def _get_tree_statements(self, max_depth, depth, verbose):
        if max_depth is not None and max_depth == 0:
            return []

        next_depth = depth + 1
        next_max_depth = None if max_depth is None else max_depth - 1

        prefix = '' if depth <= 2 else '   ' * (depth - 2)
        prefix += '' if depth == 1 else '|- '
        statements = [prefix + self.get_string_repr(verbose=verbose)]
        for n in self.children:
            statements += n._get_tree_statements(next_max_depth, next_depth, verbose)

        return statements


class Sentence(object):
    """
    Represents one Sentence in the analyzed natural language.
    Each sentence has several words, represented in a `Tree`.
    """

    def __init__(self):
        # the actual sentence (text)
        self.content = None

        # the root `Tree` node
        self.root = None

    def __repr__(self):
        return self.get_string_repr(verbose=True)

    def get_string_repr(self, verbose=True):
        """
        Gets a string (tree) representation for the Sentence
        :param verbose: Returns a more detailed string for each `Tree` node if this is True
        :type verbose bool

        :return: Returns a string (tree) representation for the Sentence
        :rtype str
        """
        return "Sentence: '{}'\n".format(self.content) + self.root.get_printable_tree(verbose=verbose)


class Document(object):
    """
    Represents a document, which holds multiple `Sentence`s.
    """

    def __init__(self):
        # language of the document
        self.language = None

        # list of `Sentence`s
        self.sentences = []

    def __repr__(self):
        return self.get_string_repr(verbose=True)

    def get_string_repr(self, verbose=True):
        """
        Gets a string (tree) representation for all `Sentence`s in the document
        :param verbose: Returns a more detailed string for each `Tree` node if this is True
        :type verbose bool

        :return: Returns a string (tree) representation for the Document
        :rtype str
        """
        ret = 'Document ({} sentences)\n'.format(len(self.sentences))
        for s in self.sentences:
            ret += s.get_string_repr(verbose=verbose) + '\n' + ('-' * 20) + '\n'
        return ret
