from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from failure_doctor.android_ops.business_data_binding import bind_data
from failure_doctor.android_ops.business_templates import scaffold_template
from failure_doctor.android_ops.device_farm import init_farm
from failure_doctor.android_ops.device_inventory import discover_devices
from failure_doctor.android_ops.device_lease import lease_device, release_device
from failure_doctor.android_ops.mutation_guard import evaluate_mutation_guard
from failure_doctor.android_ops.workflow_scheduler import plan_schedule, run_schedule
from tools.validation.run_android_ops_validation import main as run_android_ops_validation


class AndroidOpsV53Tests(unittest.TestCase):
    def test_cli_help_exposes_android_ops(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("android-ops", result.stdout)

        result = subprocess.run(
            [sys.executable, "-m", "failure_doctor", "android-ops", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("farm", result.stdout)
        self.assertIn("mutation-check", result.stdout)

    def test_farm_lease_scheduler_and_mutation_guard_are_safe_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_name:
            tmp = Path(tmp_name)
            farm = tmp / "farm"
            init_farm(farm)
            inventory = discover_devices(farm, tmp / "inventory")
            device_id = inventory["devices"][0]["device_id"]
            first = lease_device(farm, device_id, "task_001")
            second = lease_device(farm, device_id, "task_002")
            released = release_device(farm, device_id, "task_001")
            self.assertEqual(first["status"], "pass")
            self.assertEqual(second["status"], "blocked")
            self.assertEqual(released["status"], "pass")

            flow = tmp / "flow.yml"
            scaffold_template("post_image_text_save_draft", flow)
            csv_path = tmp / "tasks.csv"
            csv_path.write_text("task_id,title,body\ntask_001,hello,body\n", encoding="utf-8")
            bound = bind_data(flow, csv_path, tmp / "bound")
            plan = plan_schedule(farm, tmp / "bound", tmp / "plan")
            run = run_schedule(tmp / "plan", tmp / "run")
            guard = evaluate_mutation_guard(flow, tmp / "guard")

            unsafe = tmp / "unsafe.yml"
            unsafe.write_text("authorized_target: true\nsteps:\n  - action: submit price inventory\n", encoding="utf-8")
            unsafe_guard = evaluate_mutation_guard(unsafe, tmp / "unsafe_guard")

            self.assertEqual(bound["status"], "pass")
            self.assertEqual(len(plan["assignments"]), 1)
            self.assertEqual(run["status"], "pass")
            self.assertEqual(guard["status"], "pass")
            self.assertEqual(unsafe_guard["status"], "blocked")
            self.assertTrue(unsafe_guard["final_submit_blocked"])
            self.assertTrue(unsafe_guard["business_mutation_blocked"])

    def test_android_ops_validation_runner_writes_pass_report(self) -> None:
        self.assertEqual(run_android_ops_validation(), 0)
        payload = json.loads(Path("validation/android_ops_validation.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["version"], "v5.3.0")
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["total_cases"], 320)
        self.assertEqual(payload["external_api_call_count"], 0)
        self.assertEqual(payload["real_business_mutation_count"], 0)


if __name__ == "__main__":
    unittest.main()

