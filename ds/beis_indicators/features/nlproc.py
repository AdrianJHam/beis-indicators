import re
import nltk
import string
import gensim
from nltk.corpus import stopwords

try:
    stopwords.words("english")  # Raise lookup error if stop words not downloaded
except LookupError:
    nltk.download("stopwords")
    nltk.download("punkt")

stop_words = set(
    stopwords.words("english") + list(string.punctuation) + ["\\n"] + ["quot"]
)

regex_str = [
    "http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|" "[!*\(\),](?:%[0-9a-f][0-9a-f]))+",
    "(?:\w+-\w+){2}",
    "(?:\w+-\w+)",
    "(?:\\\+n+)",
    "(?:@[\w_]+)",
    "<[^>]+>",
    "(?:\w+'\w)",
    "(?:[\w_]+)",
    "(?:\S)",
]

# Create the tokenizer which will be case insensitive and will ignore space.
tokens_re = re.compile(
    r"(" + "|".join(regex_str) + ")", re.VERBOSE | re.IGNORECASE
)


def tokenize_document(text):
    """Preprocess a whole raw document.

    Args:
        text (:obj:`str`): Raw string of text.

    Return:
        List of preprocessed and tokenized documents

    """
    return [
        clean_and_tokenize(sentence) for sentence in nltk.sent_tokenize(text)
    ]


def clean_and_tokenize(text):
    """Preprocess a raw string/sentence of text.

    Args:
       text (:obj:`str`): Raw string of text.

    Return:
       tokens (:obj:`list` of :obj:`str`): Preprocessed tokens.

    """
    tokens = tokens_re.findall(text)
    _tokens = [t.lower() for t in tokens]
    filtered_tokens = [
        token.replace("-", "_")
        for token in _tokens
        if len(token) > 2
        and token not in stop_words
        and not any(x in token for x in string.digits)
        and any(x in token for x in string.ascii_lowercase)
    ]
    return filtered_tokens


def build_ngrams(documents, n=3, **kwargs):
    """Create ngrams using Gensim's phrases.

    Args:
        documents (:obj:`list` of token lists): List of preprocessed and
            tokenized documents.
        n (:obj:`int`): The `n` in n-gram.

    """
    # Check whether "level" was passed as an argument
    if "level" not in kwargs:
        level = 2
    else:
        level = kwargs["level"]
    # Get the bigrams
    phrases = gensim.models.Phrases(
        documents, min_count=2, threshold=1, delimiter=b"_"
    )
    bigram = gensim.models.phrases.Phraser(phrases)
    docs_bi = [bigram[doc] for doc in documents]
    # If finished
    if level == n:
        return docs_bi
    # Otherwise, keep processing until n-grams satisfied
    return build_ngrams(docs_bi, n=n, level=level + 1)
