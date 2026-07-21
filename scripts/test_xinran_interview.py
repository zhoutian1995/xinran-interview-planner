import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CLI = ROOT / "xinran_interview.py"


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], text=True, encoding="utf-8", capture_output=True)

    def test_help(self):
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("昕然有约", result.stdout)

    def test_init_score_validate_render(self):
        with tempfile.TemporaryDirectory() as temp:
            packet_path = Path(temp) / "research.json"
            plan_path = Path(temp) / "plan.md"
            result = self.run_cli("init", "--guest", "测试嘉宾", "--identity", "艺术家", "--output", str(packet_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            packet["sources"] = [{"title": "来源", "url": "https://example.com", "published_at": "2026-07-01", "accessed_at": "2026-07-21"}]
            packet["facts"] = [{"label": "已证实", "claim": "测试事实"}]
            packet["topic_candidates"] = [{"title": "AI 与艺术创作", "risk": "版权边界", "scores": {key: 4 for key in ("guest_fit", "audience_need", "timeliness", "depth", "distribution", "safety")}}]
            packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(self.run_cli("score", "--input", str(packet_path)).returncode, 0)
            self.assertEqual(self.run_cli("validate", "--input", str(packet_path)).returncode, 0)
            self.assertEqual(self.run_cli("render", "--input", str(packet_path), "--output", str(plan_path)).returncode, 0)
            self.assertIn("昕然有约 × 测试嘉宾", plan_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
