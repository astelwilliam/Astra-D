from memory_nlp import nlp

doc = nlp("John is building Astra-D in Kochi.")

for token in doc:
    print(token.text, token.pos_)