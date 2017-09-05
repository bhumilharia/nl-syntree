import os

from google.cloud import language
from google.cloud.language import enums, types

from library.document import Tree, Document, Sentence
from library.operations import find_generic_triples_multi_criteria

DEBUG = False
POS_TAGS = {v: k for k, v in enums.PartOfSpeech.Tag.__dict__.items() if not k.startswith('_')}
LABELS = {v: k for k, v in enums.DependencyEdge.Label.__dict__.items() if not k.startswith('_')}


def setup_credentials(credential_path):
    """
    Set up Google Cloud API credentials by setting environment variable
    :param credential_path: full path to secret key file
    :type credential_path str
    """
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path


def create_client():
    """
    Construct a Google API client
    :return: Google API client
    :rtype language.LanguageServiceClient
    """
    client = language.LanguageServiceClient()
    return client


def analyze_syntax(client, text, doc_type=enums.Document.Type.PLAIN_TEXT):
    """
    Analyze a text document using Google Cloud Natural Language analyze_syntax
    API, and return the response

    :param client: client to use for API call
    :type client language.LanguageServiceClient
    :param text: the text to analyze
    :type text str
    :param doc_type: type of document in `text`
    :type doc_type enums.Document.Type

    :return: API response
    """
    document = types.Document(content=text, type=doc_type)
    response = client.analyze_syntax(document)
    return response


def _create_tree(token_index, all_tokens):
    token = all_tokens[token_index]
    if DEBUG:
        if token.dependency_edge.head_token_index == token_index:
            p_txt = '*'
        else:
            p_txt = all_tokens[token.dependency_edge.head_token_index].text.content
        print("Creating tree node {}: {} \t{}\tp:{}".format(
            token_index, LABELS[token.dependency_edge.label], token.text.content, p_txt))

    tree = Tree()
    tree.index = token_index
    tree.label = token.dependency_edge.label
    tree.content = token.text.content
    tree.lemma = token.lemma
    tree.pos_tag = token.part_of_speech.tag
    tree.children = [_create_tree(i, all_tokens) for i, t in enumerate(all_tokens)
                     if t.dependency_edge.label != enums.DependencyEdge.Label.ROOT
                     and t.dependency_edge.head_token_index == token_index]

    return tree


def create_nlst_document_from_response(response):
    doc = Document()
    doc.language = response.language

    sentence_root_indices = [index for index, t in enumerate(response.tokens)
                             if t.dependency_edge.label == enums.DependencyEdge.Label.ROOT]

    for sentence, root_index in zip(response.sentences, sentence_root_indices):
        sentence_tree = Sentence()
        sentence_tree.content = sentence.text.content
        sentence_tree.root = _create_tree(root_index, response.tokens)
        doc.sentences.append(sentence_tree)

    return doc


def find_verb_triples(doc_or_sentence, active_voice=True, passive_voice=True):
    """
    Iterator which returns triples (subject, verb, object) of nodes

    :param doc_or_sentence: the Document or Sentence to operate on
    :type doc_or_sentence library.document.Document|library.document.Sentence

    :param active_voice: include triples with active voice
    :type active_voice bool

    :param passive_voice: include triples with passive voice
    :type passive_voice bool

    :return: iterator that yields triples
    :rtype list of tuple
    """
    if active_voice:
        gen = find_generic_triples_multi_criteria(
            doc_or_sentence,
            [enums.DependencyEdge.Label.NSUBJ],
            [enums.PartOfSpeech.Tag.VERB],
            [enums.DependencyEdge.Label.DOBJ, enums.DependencyEdge.Label.PREP])

        for value in gen:
            yield value

    if passive_voice:
        gen = find_generic_triples_multi_criteria(
            doc_or_sentence,
            [enums.DependencyEdge.Label.NSUBJPASS],
            [enums.PartOfSpeech.Tag.VERB],
            [enums.DependencyEdge.Label.POBJ, enums.DependencyEdge.Label.PREP])

        for value in gen:
            yield value


def verb_filter(tree, current_node):
    """
    Filter that allows only those nodes which are Verbs

    :param tree: the root Tree node which is being walked
    :param current_node: the node being filtered
    :return: True if current_node satisfies filter, else False
    :rtype bool
    """
    if current_node.pos_tag == enums.PartOfSpeech.Tag.VERB:
        return True
    return False
