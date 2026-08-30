REWRITER_SYSTEM_PROMPT = """Rewrite the user's question into a precise, self-contained
retrieval query. Resolve vague pronouns (it, that, this) only if the intent is
obvious from the question itself — do not invent context that isn't there.
Output ONLY the rewritten question, nothing else."""


def build_rewriter_prompt(query: str) -> str:
    return f"Question: {query}"
