from dataclasses import dataclass, field


@dataclass(slots=True)
class Context:

    use_memory: bool = False
    use_documents: bool = False
    use_notes: bool = False
    use_tasks: bool = False

    memories: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)