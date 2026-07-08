from astra_d.memory.engine import MemoryEngine
from prompt_builder import PromptBuilder
from retrieval_engine import RetrievalEngine


def test_prompt_without_memories():
    engine = MemoryEngine(load_existing=False)

    retrieval = RetrievalEngine(engine.semantic_memory)
    builder = PromptBuilder(retrieval)

    prompt = builder.build("Hello")

    assert prompt == "Hello"


def test_prompt_contains_relevant_memory():
    engine = MemoryEngine(load_existing=False)

    engine.remember("I use Python every day.")

    retrieval = RetrievalEngine(engine.semantic_memory)
    builder = PromptBuilder(retrieval)

    prompt = builder.build("What language do I use?")

    assert "Relevant memories:" in prompt
    assert "Python" in prompt
    assert "Current user message:" in prompt


def test_original_message_is_preserved():
    engine = MemoryEngine(load_existing=False)

    engine.remember("I own an RTX 2050.")

    retrieval = RetrievalEngine(engine.semantic_memory)
    builder = PromptBuilder(retrieval)

    message = "What GPU do I own?"

    prompt = builder.build(message)

    assert message in prompt