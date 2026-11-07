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
        self.assertIn('git worktree add -b "$STATE_BRANCH" "$STATE_WORKTREE" main', self.workflow)
        self.assertNotIn("git push origin main", self.workflow)
        self.assertNotIn("git rebase origin/main", self.workflow)

    def test_live_collector_does_not_run_regression_tests(self):
        self.assertNotIn("Run SPUTNIK Telegram delivery regression tests", self.workflow)
        self.assertNotIn("python -m unittest", self.workflow)
        self.assertIn("run: python trump_tracker.py", self.workflow)

    def test_regression_tests_remain_in_dedicated_ci_workflow(self):
        workflow = Path(".github/workflows/sputnik_tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("python -m unittest discover -s tests", workflow)

    def test_persistence_requires_successful_state_restore(self):
        self.assertIn(
            "if: always() && steps.restore_state.outcome == 'success'",
            self.workflow,
        )

    def test_state_write_permission_is_explicit_for_dedicated_branch_push(self):
        self.assertIn("permissions:", self.workflow)
        self.assertIn("  contents: write", self.workflow)



    def test_daily_summary_prefers_dedicated_state_and_falls_back_to_main(self):
        summary = Path(".github/workflows/daily-summary.yml").read_text(encoding="utf-8")
        dedicated = "trump-trucker/sputnik-state/sputnik_state.json"
        fallback = "trump-trucker/main/sputnik_state.json"
        self.assertIn(dedicated, summary)
        self.assertIn(fallback, summary)
        self.assertLess(summary.index(dedicated), summary.index(fallback))

    def test_telegram_listener_prefers_dedicated_state_and_falls_back_to_main(self):
        listener = Path("telegram_listener.py").read_text(encoding="utf-8")
        dedicated = "trump-trucker/sputnik-state/sputnik_state.json"
        fallback = "trump-trucker/main/sputnik_state.json"
        self.assertIn(dedicated, listener)
        self.assertIn(fallback, listener)
        self.assertIn("REMOTE_STATE_FALLBACK_URL", listener)
        self.assertLess(listener.index(dedicated), listener.index(fallback))

    def test_ci_covers_all_state_migration_files(self):
        ci = Path(".github/workflows/sputnik_tests.yml").read_text(encoding="utf-8")
        for path in (
            "tests/test_sputnik_state_branch_workflow.py",
            ".github/workflows/trump_tracker.yml",
        ):
            self.assertGreaterEqual(ci.count(f'"{path}"'), 2)
        self.assertIn('".github/workflows/daily-summary.yml"', ci)
        self.assertIn('"telegram_listener.py"', ci)

if __name__ == "__main__":
    unittest.main()
