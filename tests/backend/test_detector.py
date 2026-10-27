from app.detector import detect


def test_detection_contains_matching_evidence_and_capped_confidence():
    result = detect({
        "headers": {"server": "nginx"},
        "html": '<meta name="generator" content="WordPress"><script src="/wp-content/app.js"></script>',
        "meta": [{"name": "generator", "content": "WordPress"}],
        "scripts": ["/wp-content/app.js"],
        "styles": [],
    })
    wordpress = next(item for item in result if item.name == "WordPress")
    assert wordpress.confidence == "high"
    assert wordpress.score == 100
    assert any(item.source == "meta_generator" and "WordPress" in item.matched for item in wordpress.evidence)
    assert any(item.name == "Nginx" for item in result)
