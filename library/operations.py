import itertools

from library.document import Document, Sentence


def find_generic_triples(doc_or_sentence, left_label, head_pos_tag, right_label):
    """
    Iterator which returns triples (left, middle, right) of nodes such that
    middle is the direct parent of left and middle, and (left, middle, right)
    match left_label, head_pos_tag, and right_label respectively.

    :param doc_or_sentence: the Document or Sentence to operate on
    :type doc_or_sentence library.document.Document|library.document.Sentence

    :param left_label: the labels to match left.label with
    :type left_label list

    :param head_pos_tag: the pos_tags to match left.pos_tag with
    :type head_pos_tag list

    :param right_label: the labels to match right.label with
    :type right_label list

    :return: iterator that yields triples
    :rtype list of tuple
    """
    if isinstance(doc_or_sentence, Document):
        sentences = doc_or_sentence.sentences
    elif isinstance(doc_or_sentence, Sentence):
        sentences = [doc_or_sentence]
    else:
        raise TypeError('doc_or_sentence')

    for sentence in sentences:
        for node in sentence.root.walk():
            if node.pos_tag != head_pos_tag:
                continue

            left_deps = []
            right_deps = []

            for child in node.children:
                if child.label == left_label:
                    left_deps.append(child)
                elif child.label == right_label:
                    right_deps.append(child)

            for left_dep in left_deps:
                for right_dep in right_deps:
                    yield (left_dep, node, right_dep)


def find_generic_triples_multi_criteria(
        doc_or_sentence, left_labels, head_pos_tags, right_labels):
    """
    Iterator which returns triples (left, middle, right) of nodes such that
    middle is the direct parent of left and middle, and (left, middle, right)
    belong to the cross product of (left_labels, head_pos_tags, and right_labels)
    respectively.

    :param doc_or_sentence: the Document or Sentence to operate on
    :type doc_or_sentence library.document.Document|library.document.Sentence

    :param left_labels: the labels to match left.label with
    :type left_labels list

    :param head_pos_tags: the pos_tags to match left.pos_tag with
    :type head_pos_tags list

    :param right_labels: the labels to match right.label with
    :type right_labels list

    :return: iterator that yields triples
    :rtype list of tuple
    """
    for left, head, right in itertools.product(left_labels, head_pos_tags, right_labels):
        for val in find_generic_triples(doc_or_sentence, left, head, right):
            yield val
