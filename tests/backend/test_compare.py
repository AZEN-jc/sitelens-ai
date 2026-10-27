from app.compare import compare_results


def test_comparison_describes_absence_as_not_observed():
    previous = [{"name": "React", "evidence": ["script:/assets/app.js"]}]
    current = []
    comparison = compare_results(previous, current)
    assert comparison["not_observed_now"] == ["React"]
    assert "removed" not in str(comparison).lower()
