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

    def test_scheduled_run_history_is_logged_without_blocking_collection(self):
        self.assertIn("actions: read", self.workflow)
        self.assertIn("actions/workflows/trump_tracker.yml/runs?event=schedule&per_page=20", self.workflow)
        self.assertIn("SPUTNIK_SCHEDULE_RUN", self.workflow)
        self.assertIn("SPUTNIK_SCHEDULE_GAP", self.workflow)
        self.assertIn("SPUTNIK scheduled-run history unavailable", self.workflow)
        self.assertIn("SPUTNIK scheduled-run history response unreadable", self.workflow)
        self.assertIn("SPUTNIK scheduled-run history response invalid", self.workflow)
        self.assertLess(
            self.workflow.index("Report recent scheduled collector runs"),
            self.workflow.index("Run SPUTNIK (Render-independent)"),
        )


if __name__ == "__main__":
    unittest.main()
