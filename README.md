## Overview
Library to make working with Natural Language syntax trees easier. Currently supports working with Google Cloud Natural Language `analyze_syntax` API.

I've created this as a part of my current experiments with natural language syntax analysis, and I currently use this only for prototyping. This library does not have test coverage at the moment, and has not been used in production.

Despite the fact that I've currently only added code for Google's parser, the core classes/interfaces have no dependency on Google's API / algorithms specifically, so this could be used with other syntax parsers as well.

You're free to use this code in any manner you'd like, though if you make improvements to this code, I'll appreciate pull requests. This is not a requirement, but definitely a nice-to-have.


## Design and Usage
There are three main classes: `Document`, which represents one document, which may in turn contain several sentences. Each `Sentence` consists of many words, which are represented in a dependency tree. A `Sentence` object only contains the reference to the root `Tree` node.

To use this library, simply clone it, and install the requirements
```
pip install -r requirements.txt
```

If you're not set up with the google API, see section at the end of this document, then come back here.

Once you're set up, simply initialize the client and fire away

```python
from providers.google_cloud import create_client
client = create_client()
```

Use the client to analyze syntax of a document using the API.
```python
from providers.google_cloud import analyze_syntax, create_nlst_document_from_response

text = "The fox was quick. The dog was lazy."
api_response = analyze_syntax(client, text)
doc = create_nlst_document_from_response(api_response)
```

Use the resulting `doc` object for your custom analysis.
```python
from providers.google_cloud import find_verb_triples
for l, m, r in find_verb_triples(doc):
    print('{:<15s} | {:<20s} | {:<28s}'.format(l.content, m.content, r.content))
```

## Setting up to use the Google API
You can sign up for (and get started with) Google's natural language APIs here: https://cloud.google.com/natural-language/

Follow their steps, create a project, download their API keys. To set up the connection, you'll have to set up the `GOOGLE_APPLICATION_CREDENTIALS` environment variable. You can do that in your environment, or a helper method to do it directly in code is provided

```python
from providers.google_cloud import setup_credentials
setup_credentials('/path/to/key.json')
```

