from astra_d.memory.nlp import analyze
from astra_d.memory.semantic import SemanticMemory

memory = SemanticMemory()

text = "John is building Astra-D in Kochi."

result = analyze(text)

entry = memory.store(text, result)

print("Stored Memory")
print("----------------")
print("ID:", entry.id)
print("Text:", entry.text)
print("Entities:", entry.entities)
print("Keywords:", entry.keywords)
print("Timestamp:", entry.timestamp)

print("\nMemory Count:", memory.count())

print("\nAll Memories:")
for mem in memory.get_all():
    print(mem)