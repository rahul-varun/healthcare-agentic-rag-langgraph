from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_documents_finds_ingested_markdown_file():
    response = client.get("/api/documents")
    assert response.status_code == 200
    names = [d["name"] for d in response.json()["documents"]]
    assert "revenue.md" in names


def test_list_documents_excludes_dotfiles():
    response = client.get("/api/documents")
    names = [d["name"] for d in response.json()["documents"]]
    assert all(not name.startswith(".") for name in names)
