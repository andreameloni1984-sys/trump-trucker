from pathlib import Path
import unittest


class SputnikStateBranchWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = Path(".github/workflows/trump_tracker.yml").read_text(
            encoding="utf-8"
        )

    def test_state_is_restored_before_the_collector_runs(self):
        self.assertIn('STATE_BRANCH="sputnik-state"', self.workflow)
        self.assertIn(
            'git show "refs/remotes/origin/${STATE_BRANCH}:sputnik_state.json" > sputnik_state.json',
            self.workflow,
        )
        self.assertLess(
            self.workflow.index("Restore SPUTNIK state from dedicated branch"),
            self.workflow.index("Run SPUTNIK (Render-independent)"),
        )

    def test_state_persistence_targets_only_the_dedicated_branch(self):
        self.assertIn('git push origin HEAD:"refs/heads/${STATE_BRANCH}"', self.workflow)
        self.assertNotIn("git push origin main", self.workflow)
        self.assertNotIn("git rebase origin/main", self.workflow)

    def test_live_collector_does_not_run_regression_tests(self):
        self.assertNotIn(
            "Run SPUTNIK Telegram delivery regression tests",
            self.workflow,
        )
        self.assertNotIn(
            "python -m unittest tests/test_telegram_delivery.py",
            self.workflow,
        )
        self.assertIn("run: python trump_tracker.py", self.workflow)

    def test_regression_tests_remain_in_dedicated_ci_workflow(self):
        workflow = Path(".github/workflows/sputnik_tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('python -m unittest discover -s tests', workflow)

    def test_persistence_requires_successful_state_restore(self):
        self.assertIn(
            "if: always() && steps.restore_state.outcome == 'success'",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
