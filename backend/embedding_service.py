from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

embedding_cache = {}


def get_embedding(text: str):

    if text not in embedding_cache:

        embedding_cache[text] = model.encode(
            text,
            convert_to_tensor=True
        )

    return embedding_cache[text]

def cache_note_embedding(title: str, content: str):

    text = f"{title} {content}"

    get_embedding(text)


def remove_note_embedding(title: str, content: str):

    text = f"{title} {content}"

    embedding_cache.pop(text, None)


def cosine_similarity(a, b):

    return float(
        cos_sim(a, b)
    )