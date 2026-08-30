from app.tools.web_tool import _is_allowed


def test_no_allowlist_allows_everything():
    assert _is_allowed("https://anything.example.com/page", []) is True


def test_allowlist_permits_matching_domain():
    assert _is_allowed("https://www.reuters.com/business/", ["reuters.com"]) is True


def test_allowlist_blocks_non_matching_domain():
    assert _is_allowed("https://random-blog.example/post", ["reuters.com", "bloomberg.com"]) is False
