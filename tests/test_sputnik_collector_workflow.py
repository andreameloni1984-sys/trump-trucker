from pathlib import Path
import unittest


class ScheduledCollectorWorkflowTests(unittest.TestCase):
    def test_production_collector_does_not_run_regression_tests(self):
        workflow = Path(".github/workflows/trump_tracker.yml").read_text(
            encoding="utf-8"
        )
        self.assertNotIn(
            "Run SPUTNIK Telegram delivery regression tests", workflow
        )
        self.assertNotIn(
            "python -m unittest tests/test_telegram_delivery.py", workflow
        )
        self.assertIn("run: python trump_tracker.py", workflow)

    def test_regression_suite_remains_in_dedicated_ci_workflow(self):
        workflow = Path(".github/workflows/sputnik_tests.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn('python -m unittest discover -s tests -p "test_*.py" -v', workflow)


if __name__ == "__main__":
    unittest.main()
