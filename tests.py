import re

from rag import (
    REFUSAL,
    ask,
    chunk_text,
    get_collection,
)

# ---------- Edit these to match the content of your documents/ folder ----------

IN_SCOPE_QUESTIONS = [
    "What happens if my GPA falls below the minimum?",
    "What are the graduation requirements?",
    "How do I register for courses?",
    "What is academic probation?",
]

OUT_OF_SCOPE_QUESTIONS = [
    "what is my name?",
    "how old am I?",
    "Who won the World Cup?",
    "What is the weather today?",
    "What is the capital of France?",
    "",
]

# ---------- Tiny test runner ----------

results = []


def check(name, condition, detail=""):
    results.append(bool(condition))
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f"  ->  {detail}" if detail and not condition else ""))


# ---------- Chunking tests (no documents needed) ----------

def test_chunking():
    sample = (
        "Academic Probation\n"
        "\n"
        "A student is placed on academic probation when the cumulative GPA falls\n"
        "below 2.0. The student must raise the GPA within two semesters.\n"
        "\n"
        "1. Registration is open during the first week.\n"
        "2. Late registration requires a fee.\n"
    )
    chunks = chunk_text(sample)

    check("chunking: produces chunks", len(chunks) >= 1)
    check(
        "chunking: heading merged into the paragraph below it",
        any(c.startswith("Academic Probation A student") for c in chunks),
        str(chunks),
    )
    check(
        "chunking: wrapped lines are rejoined",
        any("falls below 2.0." in c for c in chunks),
        str(chunks),
    )
    check(
        "chunking: numbered items become separate chunks",
        any(c.startswith("1. Registration") for c in chunks)
        and any(c.startswith("2. Late registration") for c in chunks),
        str(chunks),
    )
    check(
        "chunking: every chunk ends at a sentence boundary",
        all(re.search(r"[.!?؟]$", c) for c in chunks),
        str(chunks),
    )

    long_paragraph = " ".join(
        f"Rule number {i} states that students must follow the regulation." for i in range(40)
    )
    long_chunks = chunk_text(long_paragraph, max_chars=300)
    check("chunking: long paragraph is split", len(long_chunks) > 1)
    check(
        "chunking: long paragraph split only at sentence ends",
        all(c.endswith(".") and c.startswith("Rule number") for c in long_chunks),
        str(long_chunks[:2]),
    )


# ---------- Retrieval and refusal tests (use your real documents) ----------

def test_rebuild_is_safe():
    try:
        get_collection(force_rebuild=True)
        get_collection(force_rebuild=True)
        ok = True
    except Exception as e:  # noqa: BLE001
        ok, detail = False, repr(e)
    check("chroma: rebuilding the collection twice does not raise", ok, "" if ok else detail)


def test_out_of_scope():
    for q in OUT_OF_SCOPE_QUESTIONS:
        answer, sources = ask(q)
        check(
            f"refusal: {q!r}",
            answer == REFUSAL and sources == [],
            f"got {answer[:60]!r}",
        )


def test_in_scope():
    for q in IN_SCOPE_QUESTIONS:
        answer, sources = ask(q)
        check(f"answers: {q!r}", answer != REFUSAL and len(sources) == 1, "was refused")
        check(
            f"complete sentence: {q!r}",
            bool(re.search(r"[.!?؟]$", answer.strip())),
            f"ends with {answer.strip()[-20:]!r}",
        )


if __name__ == "__main__":
    test_chunking()
    test_rebuild_is_safe()
    test_out_of_scope()
    test_in_scope()

    passed, total = sum(results), len(results)
    print(f"\n{passed}/{total} checks passed")
    raise SystemExit(0 if passed == total else 1)