"""Offline standard-library tests for aggregate project metrics publication."""
import importlib.util
import pathlib
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

    def test_reject_negative(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,-1,MASTER,a,b\n")

    def test_reject_path_token(self):
        with self.assertRaises(ValueError):
            self.check("year,table,records,scope,verified_by,evidence_id\n2006,DEMO,1,MASTER,C:/private/file,abc\n")


if __name__ == "__main__":
    unittest.main()
