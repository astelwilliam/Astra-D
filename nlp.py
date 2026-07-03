import spacy

nlp = spacy.load("en_core_web_sm")

def analyze(text: str):
    doc = nlp(text)

    return {
        "entities": [(e.text, e.label_) for e in doc.ents],
        "noun_chunks": [c.text for c in doc.noun_chunks],
        "keywords": [
            t.lemma_
            for t in doc
            if not t.is_stop and not t.is_punct
        ],
    }