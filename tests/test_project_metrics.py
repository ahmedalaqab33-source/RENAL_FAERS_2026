"""Offline standard-library tests for aggregate project metrics publication."""
import importlib.util
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("metrics", ROOT / "tools" / "build_project_metrics.py")
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)


class MetricsTests(unittest.TestCase):
    def check(self, csv_text):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "metrics.csv"
            path.write_text(csv_text, encoding="utf-8")
            return metrics.render(path)

    def test_valid_aggregate(self):
        result = self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,323207,MASTER,reviewer1,QC2006\n")
        self.assertIn("323,207", result)
        self.assertIn("1 / 207", result)

    def test_reject_unapproved_columns(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id,patient_id\n2006,DEMO,1,MASTER,a,b,123\n")

    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,a,b\n2006,DEMO,2,MASTER,a,b\n")

    def test_reject_extra_row_field(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,a,b,unexpected\n")

    def test_reject_missing_row_field(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,a\n")

    def test_reject_non_ascii_numbers(self):
        for year, count in [("٢٠٠٦", "1"), ("2006", "١")]:
            with self.subTest(year=year, count=count), self.assertRaises(ValueError):
                self.check(f"year,table,records,scope,verified_by,evidence_id\n{year},DEMO,{count},MASTER,a,b\n")

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,-1,MASTER,a,b\n")

    def test_reject_path_token(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,C:/private/file,abc\n")

    def test_cli_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / "metrics.csv"
            output = pathlib.Path(directory) / "existing.md"
            source.write_text("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,a,b\n", encoding="utf-8")
            output.write_bytes(b"EXISTING_ARTIFACT")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/build_project_metrics.py"), "--input", str(source), "--output", str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b"EXISTING_ARTIFACT")

    def test_cli_invalid_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / "invalid.csv"
            output = pathlib.Path(directory) / "preview.md"
            source.write_text("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,a,b,unexpected\n", encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/build_project_metrics.py"), "--input", str(source), "--output", str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
