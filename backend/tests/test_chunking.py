from app.ingestion.chunking import chunk_text


def test_short_text_is_single_chunk():
    assert chunk_text("hello world") == ["hello world"]


def test_empty_text_is_no_chunks():
    assert chunk_text("") == []


def test_long_text_is_split_with_overlap():
    text = ("Sentence one. " * 40) + ("\n\n" + "Sentence two. " * 40)
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 220 for c in chunks)
