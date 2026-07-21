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
            packet["hotspot_candidates"] = []
            for index in range(4):
                packet["hotspot_candidates"].append({
                    "id": f"hotspot-{index}",
                    "title": f"热点{index}",
                    "reason": "近期出现新增事件，多方持续讨论，并影响目标观众的现实选择。",
                    "lifecycle": "扩散期",
                    "source_refs": [0, 0, 0],
                    "scores": {key: 4 for key in ("recency", "source_diversity", "cross_platform", "momentum", "audience_relevance", "interviewability")},
                    "interview_topics": [{
                        "question": f"具体问题{topic_index}",
                        "recommended_guests": ["一线从业者"],
                        "guest_reason": "有一手经历和真实结果",
                        "evidence_target": "成本、结果和失败案例"
                    } for topic_index in range(5)]
                })
            packet_path.write_text(json.dumps(packet, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(self.run_cli("score", "--input", str(packet_path)).returncode, 0)
            self.assertEqual(self.run_cli("validate", "--input", str(packet_path)).returncode, 0)
            self.assertEqual(self.run_cli("render", "--input", str(packet_path), "--output", str(plan_path)).returncode, 0)
            self.assertIn("昕然有约 × 测试嘉宾", plan_path.read_text(encoding="utf-8"))

    def test_topics_filter(self):
        result = self.run_cli("topics", "--tag", "老爸评测", "--keyword", "机器人")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(any(item["id"] == "robot-buying-guide" for item in data))


if __name__ == "__main__":
    unittest.main()
