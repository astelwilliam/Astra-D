from memory_nlp import _NLP

doc = _NLP("John is building Astra-D in Kochi.")

for token in doc:
    print(token.text, token.pos_)