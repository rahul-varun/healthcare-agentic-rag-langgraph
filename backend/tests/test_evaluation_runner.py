from app.evaluation.runner import EvalQuestion, evaluate_retrieval, is_relevant


def _question():
    return EvalQuestion(question="q", expected_document="revenue.md", expected_heading_path=["Revenue", "Drivers"])


def test_is_relevant_matches_document_and_heading():
    metadata = {"document": "revenue.md", "heading_path": ["Revenue", "Drivers"]}
    assert is_relevant(metadata, _question()) is True


def test_is_relevant_rejects_wrong_document():
    metadata = {"document": "other.md", "heading_path": ["Revenue", "Drivers"]}
    assert is_relevant(metadata, _question()) is False


def test_is_relevant_rejects_wrong_heading():
    metadata = {"document": "revenue.md", "heading_path": ["Revenue", "Q1"]}
    assert is_relevant(metadata, _question()) is False


def test_is_relevant_matches_pdf_style_document_name_key():
    q = EvalQuestion(question="q", expected_document="report.pdf", expected_heading_path=None)
    assert is_relevant({"document_name": "report.pdf", "page": 3}, q) is True


def test_evaluate_retrieval_perfect_retriever():
    dataset = [_question()]

    def retrieve_fn(question, top_k):
        return [{"metadata": {"document": "revenue.md", "heading_path": ["Revenue", "Drivers"]}}]

    result = evaluate_retrieval(dataset, retrieve_fn)
    assert result["aggregate"]["hit_rate"] == 1.0
    assert result["aggregate"]["reciprocal_rank"] == 1.0
    assert result["n_questions"] == 1


def test_evaluate_retrieval_useless_retriever():
    dataset = [_question()]

    def retrieve_fn(question, top_k):
        return [{"metadata": {"document": "unrelated.md"}}]

    result = evaluate_retrieval(dataset, retrieve_fn)
    assert result["aggregate"]["hit_rate"] == 0.0
    assert result["aggregate"]["reciprocal_rank"] == 0.0
