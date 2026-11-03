import re
from pathlib import Path


def _event_path_lists(workflow_text):
    blocks = re.findall(
        r"(?ms)^  (?:pull_request|push):\n(.*?)(?=^  [A-Za-z_][\w-]*:|\Z)",
        workflow_text,
    )
    path_lists = []
    for block in blocks:
        match = re.search(
            r"(?ms)^    paths:\n(.*?)(?=^    [A-Za-z_][\w-]*:|\Z)",
            block,
        )
        if match:
            path_lists.append(re.findall(r'^\s+- "([^"]+)"\s*$', match.group(1), re.M))
    return path_lists


def test_sputnik_workflow_event_path_filters_have_no_duplicate_entries():
    for workflow in (
        ".github/workflows/sputnik_tests.yml",
        ".github/workflows/sputnik_menu_tests.yml",
    ):
        path_lists = _event_path_lists(Path(workflow).read_text(encoding="utf-8"))
        assert path_lists, f"No event path filters found in {workflow}"
        for paths in path_lists:
            assert len(paths) == len(set(paths)), f"Duplicate path in {workflow}: {paths}"


def test_sputnik_workflow_filters_keep_action_reaction_and_catalyst_coverage():
    ranking = Path(".github/workflows/sputnik_tests.yml").read_text(encoding="utf-8")
    menu = Path(".github/workflows/sputnik_menu_tests.yml").read_text(encoding="utf-8")

    assert "tests/test_sputnik_action_reaction.py" in ranking
    assert "sputnik_action_reaction.py" in ranking
    assert "tests/test_sputnik_catalyst.py" in menu
