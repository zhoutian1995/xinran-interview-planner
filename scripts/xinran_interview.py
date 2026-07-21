#!/usr/bin/env python3
"""Deterministic helpers for the xinran-interview-planner skill."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

PILLARS = {
    "education-family": "教育与家庭",
    "career-wealth": "事业与财富",
    "women-growth": "女性与成长",
    "circles-life": "圈层与人生",
    "xinran-personal": "昕然个人内容",
    "ai-robotics": "AI 与机器人",
}

SCORE_FIELDS = ("guest_fit", "audience_need", "timeliness", "depth", "distribution", "safety")
HOTSPOT_SCORE_FIELDS = ("recency", "source_diversity", "cross_platform", "momentum", "audience_relevance", "interviewability")
FACT_LABELS = {"已证实", "嘉宾自述", "媒体报道", "待核实", "策划假设"}
TOPIC_LIBRARY = Path(__file__).resolve().parent.parent / "references" / "topic-library.json"


def dump(data: Any, path: str | None = None) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if path:
        Path(path).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


def load(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_topics() -> list[dict[str, Any]]:
    return json.loads(TOPIC_LIBRARY.read_text(encoding="utf-8"))


def filter_topics(tags: list[str] | None = None, keyword: str = "", pillar: str = "") -> list[dict[str, Any]]:
    wanted = [item.casefold() for item in (tags or [])]
    needle = keyword.casefold().strip()
    results = []
    for topic in load_topics():
        haystack = " ".join([topic.get("topic", ""), topic.get("hotspot", ""), *topic.get("tags", []), *topic.get("guest_types", [])]).casefold()
        if pillar and topic.get("pillar") != pillar:
            continue
        if wanted and not all(tag in haystack for tag in wanted):
            continue
        if needle and needle not in haystack:
            continue
        results.append(topic)
    return results


def search_queries(guest: str, identity: str = "", pillars: list[str] | None = None) -> list[dict[str, str]]:
    anchor = f"{guest} {identity}".strip()
    selected = pillars or list(PILLARS)
    rows = [
        {"purpose": "身份消歧", "window": "不限", "query": f'"{guest}" {identity} 主页 采访 简介'.strip()},
        {"purpose": "近期动态", "window": "近30天", "query": f'"{anchor}" 最新 采访 活动 观点'},
        {"purpose": "人物原点", "window": "长青", "query": f'"{anchor}" 经历 转折 选择 失败'},
        {"purpose": "争议与边界", "window": "不限", "query": f'"{anchor}" 争议 质疑 回应'},
    ]
    keywords = {
        "education-family": "教育 厌学 升学 亲子 家庭选择 AI教育",
        "career-wealth": "职业 创业 行业 赚钱 商业 机会",
        "women-growth": "女性 婚姻 事业 年龄 成长 重新开始",
        "circles-life": "艺术 生活方式 圈层 人生选择 作品",
        "xinran-personal": "朋友 活动 合作 共同经历",
        "ai-robotics": "AI 人工智能 机器人 具身智能 工作 创作",
    }
    for pillar in selected:
        if pillar not in PILLARS:
            raise ValueError(f"unknown pillar: {pillar}")
        rows.append({"purpose": PILLARS[pillar], "window": "近90天+长青", "query": f'"{anchor}" {keywords[pillar]}'})
    return rows


def new_packet(args: argparse.Namespace) -> dict[str, Any]:
    pillars = args.pillar or list(PILLARS)
    return {
        "schema_version": 1,
        "created": date.today().isoformat(),
        "guest": {"name": args.guest, "identity": args.identity or "", "profile_url": args.profile_url or ""},
        "episode": {"platforms": args.platform or ["小红书", "视频号"], "duration_minutes": args.duration, "publish_date": args.publish_date or ""},
        "positioning": {"account": "昕然有约", "audience": "一二线城市年轻人、中产及以上家庭", "pillars": pillars},
        "research_queries": search_queries(args.guest, args.identity or "", pillars),
        "sources": [],
        "facts": [],
        "audience_questions": [],
        "hotspot_candidates": [],
        "topic_candidates": [],
        "opening_options": [],
        "notes": [],
    }


def score_packet(packet: dict[str, Any]) -> dict[str, Any]:
    for topic in packet.get("topic_candidates", []):
        scores = topic.setdefault("scores", {})
        missing = [key for key in SCORE_FIELDS if key not in scores]
        if missing:
            topic["score_error"] = f"missing: {', '.join(missing)}"
            continue
        values = [int(scores[key]) for key in SCORE_FIELDS]
        if any(value < 1 or value > 5 for value in values):
            topic["score_error"] = "scores must be integers from 1 to 5"
            continue
        total = sum(values)
        topic["total_score"] = total
        topic.pop("score_error", None)
        if scores["guest_fit"] < 3 or scores["audience_need"] < 3:
            recommendation = "删除"
        elif scores["safety"] < 3:
            recommendation = "风险处理后再评估"
        elif total >= 24:
            recommendation = "主选题"
        elif total >= 20:
            recommendation = "有条件主选题"
        elif total >= 15:
            recommendation = "备选"
        else:
            recommendation = "删除"
        topic["recommendation"] = recommendation
    packet["topic_candidates"] = sorted(packet.get("topic_candidates", []), key=lambda x: x.get("total_score", -1), reverse=True)
    return packet


def rank_hotspots(packet: dict[str, Any]) -> dict[str, Any]:
    for hotspot in packet.get("hotspot_candidates", []):
        scores = hotspot.setdefault("scores", {})
        missing = [key for key in HOTSPOT_SCORE_FIELDS if key not in scores]
        if missing:
            hotspot["score_error"] = f"missing: {', '.join(missing)}"
            continue
        values = [int(scores[key]) for key in HOTSPOT_SCORE_FIELDS]
        if any(value < 1 or value > 5 for value in values):
            hotspot["score_error"] = "hotspot scores must be integers from 1 to 5"
            continue
        hotspot["total_score"] = sum(values)
        hotspot.pop("score_error", None)
        hotspot["eligible"] = (
            hotspot["total_score"] >= 22
            and scores["audience_relevance"] >= 4
            and scores["interviewability"] >= 4
            and len(hotspot.get("source_refs", [])) >= 3
        )
    ranked = sorted(packet.get("hotspot_candidates", []), key=lambda x: x.get("total_score", -1), reverse=True)
    packet["hotspot_candidates"] = ranked
    packet["selected_hotspots"] = [item.get("id") for item in ranked if item.get("eligible")][:4]
    return packet


def validate_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    guest = packet.get("guest", {})
    if not guest.get("name"):
        errors.append("guest.name is required")
    for index, source in enumerate(packet.get("sources", []), 1):
        for field in ("title", "url", "published_at", "accessed_at"):
            if not source.get(field):
                errors.append(f"sources[{index}] missing {field}")
    for index, fact in enumerate(packet.get("facts", []), 1):
        if fact.get("label") not in FACT_LABELS:
            errors.append(f"facts[{index}] label must be one of: {', '.join(sorted(FACT_LABELS))}")
        if not fact.get("claim"):
            errors.append(f"facts[{index}] missing claim")
    for index, topic in enumerate(packet.get("topic_candidates", []), 1):
        if not topic.get("title"):
            errors.append(f"topic_candidates[{index}] missing title")
        if "score_error" in topic:
            errors.append(f"topic_candidates[{index}] {topic['score_error']}")
    selected = set(packet.get("selected_hotspots", []))
    if len(selected) != 4:
        errors.append("exactly 4 eligible hotspots must be selected")
    for index, hotspot in enumerate(packet.get("hotspot_candidates", []), 1):
        if "score_error" in hotspot:
            errors.append(f"hotspot_candidates[{index}] {hotspot['score_error']}")
        if hotspot.get("id") in selected:
            if not hotspot.get("reason"):
                errors.append(f"hotspot_candidates[{index}] missing reason")
            if not hotspot.get("lifecycle"):
                errors.append(f"hotspot_candidates[{index}] missing lifecycle")
            interview_topics = hotspot.get("interview_topics", [])
            if len(interview_topics) != 5:
                errors.append(f"hotspot_candidates[{index}] must contain exactly 5 interview_topics")
            for topic_index, interview_topic in enumerate(interview_topics, 1):
                for field in ("question", "recommended_guests", "guest_reason", "evidence_target"):
                    if not interview_topic.get(field):
                        errors.append(f"hotspot_candidates[{index}].interview_topics[{topic_index}] missing {field}")
    return errors


def md(value: Any) -> str:
    return str(value or "待补充").replace("\n", " ")


def render(packet: dict[str, Any]) -> str:
    packet = rank_hotspots(packet)
    guest = packet.get("guest", {})
    episode = packet.get("episode", {})
    topics = packet.get("topic_candidates", [])
    primary = [x for x in topics if x.get("recommendation") in {"主选题", "有条件主选题"}][:3]
    backup = [x for x in topics if x.get("recommendation") == "备选"][:2]
    selected_ids = set(packet.get("selected_hotspots", []))
    selected_hotspots = [item for item in packet.get("hotspot_candidates", []) if item.get("id") in selected_ids]
    lines = [
        f"# 昕然有约 × {md(guest.get('name'))} 访前策划",
        "",
        f"- 研究日期：{md(packet.get('created'))}",
        f"- 嘉宾身份：{md(guest.get('identity'))}",
        f"- 平台：{', '.join(episode.get('platforms', [])) or '待补充'}",
        f"- 建议时长：{md(episode.get('duration_minutes'))} 分钟",
        "",
        "## 1. 四大热点与20个采访话题",
        "",
    ]
    if selected_hotspots:
        for number, hotspot in enumerate(selected_hotspots, 1):
            lines += [
                f"### 热点{number}：{md(hotspot.get('title'))}",
                "",
                f"**热点为什么成立：** {md(hotspot.get('reason'))}",
                "",
                f"- 热度阶段：{md(hotspot.get('lifecycle'))}",
                f"- 热点评分：{md(hotspot.get('total_score'))}/30",
                "",
                "| 采访话题 | 推荐嘉宾 | 为什么适合 | 要拿到的证据 |",
                "|---|---|---|---|",
            ]
            for interview_topic in hotspot.get("interview_topics", []):
                guests = "、".join(interview_topic.get("recommended_guests", [])) if isinstance(interview_topic.get("recommended_guests"), list) else md(interview_topic.get("recommended_guests"))
                lines.append(f"| {md(interview_topic.get('question'))} | {guests} | {md(interview_topic.get('guest_reason'))} | {md(interview_topic.get('evidence_target'))} |")
            lines.append("")
    else:
        lines += ["- 尚未形成4个达到门槛的热点。", ""]
    lines += [
        "## 2. 身份核验与嘉宾画像",
        "",
    ]
    for fact in packet.get("facts", []):
        lines.append(f"- [{md(fact.get('label'))}] {md(fact.get('claim'))}")
    if not packet.get("facts"):
        lines.append("- 待补充")
    lines += ["", "## 3. 观众问题与近期热点", ""]
    for question in packet.get("audience_questions", []):
        lines.append(f"- {md(question)}")
    if not packet.get("audience_questions"):
        lines.append("- 待补充")
    lines += ["", "## 4. 话题评分", "", "| 话题 | 总分 | 建议 | 扣分/风险 |", "|---|---:|---|---|"]
    for topic in topics:
        lines.append(f"| {md(topic.get('title'))} | {md(topic.get('total_score'))} | {md(topic.get('recommendation'))} | {md(topic.get('risk'))} |")
    if not topics:
        lines.append("| 待补充 | - | - | - |")
    lines += ["", "## 5. 三个主选题与两个备选题", ""]
    for label, selected in (("主选题", primary), ("备选题", backup)):
        lines.append(f"### {label}")
        lines.append("")
        if selected:
            for topic in selected:
                lines.append(f"- **{md(topic.get('title'))}**：{md(topic.get('rationale'))}")
        else:
            lines.append("- 待补充")
        lines.append("")
    lines += [
        "## 6. 独立开场方案",
        "",
        "从故事、冲突、现场、物件、第三方问题或当下事件中选择最适合该嘉宾的一种，不套统一模板。",
        "",
        "## 7. 采访结构与追问树",
        "",
        "由 AI 围绕高分主选题补充：主问题、场景追问、证据追问、代价追问、边界追问、普通人翻译。",
        "",
        "## 8. 传播包装",
        "",
        "由 AI 根据平台补充标题、封面句、30-90 秒观点切片、2-5 分钟故事切片和评论区问题。",
        "",
        "## 9. 昕然主持人手卡",
        "",
        "由 AI 压缩：开场、必问 5 题、必追证据、敏感边界、救场问题、结尾问题。",
        "",
        "## 来源",
        "",
    ]
    for source in packet.get("sources", []):
        lines.append(f"- [{md(source.get('title'))}]({md(source.get('url'))})，发布 {md(source.get('published_at'))}，访问 {md(source.get('accessed_at'))}")
    if not packet.get("sources"):
        lines.append("- 待补充")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="xinran-interview", description="昕然有约采访策划辅助工具：生成研究包、检索计划、话题评分、校验和策划骨架。")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("help", help="显示推荐工作流和研究包字段说明")

    init = sub.add_parser("init", help="为一位嘉宾初始化 JSON 研究包")
    init.add_argument("--guest", default="待定", help="嘉宾姓名；做热点选题时可不填")
    init.add_argument("--identity", default="", help="身份线索，用于同名消歧")
    init.add_argument("--profile-url", default="", help="嘉宾主页链接")
    init.add_argument("--platform", action="append", help="目标平台，可重复")
    init.add_argument("--duration", type=int, default=30, help="预计采访分钟数，默认 30")
    init.add_argument("--publish-date", default="", help="预计发布日期 YYYY-MM-DD")
    init.add_argument("--pillar", action="append", choices=sorted(PILLARS), help="内容主线，可重复；默认全部")
    init.add_argument("--output", help="输出 JSON 文件；不填则打印到 stdout")

    queries = sub.add_parser("queries", help="生成身份消歧、人物经历和内容主线检索式")
    queries.add_argument("--guest", required=True)
    queries.add_argument("--identity", default="")
    queries.add_argument("--pillar", action="append", choices=sorted(PILLARS))
    queries.add_argument("--output")

    topics = sub.add_parser("topics", help="按嘉宾身份、关键词或内容主线筛选内置采访话题库")
    topics.add_argument("--tag", action="append", help="标签或嘉宾类型，可重复，例如 自媒体、MIT妈妈")
    topics.add_argument("--keyword", default="", help="关键词，例如 AI、机器人、短剧")
    topics.add_argument("--pillar", choices=sorted(PILLARS), default="", help="限定内容主线")
    topics.add_argument("--output")

    rank = sub.add_parser("rank-hotspots", help="按证据六维评分排序热点并选出前4名")
    rank.add_argument("--input", required=True)
    rank.add_argument("--output", help="默认覆盖输入文件；使用 - 打印到 stdout")

    score = sub.add_parser("score", help="计算 topic_candidates 六维分数和推荐级别")
    score.add_argument("--input", required=True)
    score.add_argument("--output", help="默认覆盖输入文件；使用 - 打印到 stdout")

    validate = sub.add_parser("validate", help="校验来源、事实标签和话题评分字段")
    validate.add_argument("--input", required=True)

    render_cmd = sub.add_parser("render", help="把已研究并评分的 JSON 渲染成 Markdown 策划骨架")
    render_cmd.add_argument("--input", required=True)
    render_cmd.add_argument("--output", help="输出 Markdown 文件；不填则打印到 stdout")
    return parser


def print_help_text() -> None:
    print("""昕然有约采访策划推荐流程

1. init：创建研究包。
2. 用搜索/浏览器采集候选热点及来源证据。
3. rank-hotspots：按六维证据评分选出4个热点。
4. 每个热点填写恰好5个采访话题、推荐嘉宾和匹配理由。
5. validate：检查4×5结构、来源和事实标签。
6. render：生成四大热点、20个话题和后续访前策划骨架。

话题评分字段：guest_fit、audience_need、timeliness、depth、distribution、safety，均为 1-5。
热点评分字段：recency、source_diversity、cross_platform、momentum、audience_relevance、interviewability，均为 1-5。
事实标签：已证实、嘉宾自述、媒体报道、待核实、策划假设。
""")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "help":
            print_help_text()
        elif args.command == "init":
            dump(new_packet(args), args.output)
        elif args.command == "queries":
            dump(search_queries(args.guest, args.identity, args.pillar), args.output)
        elif args.command == "topics":
            dump(filter_topics(args.tag, args.keyword, args.pillar), args.output)
        elif args.command == "rank-hotspots":
            packet = rank_hotspots(load(args.input))
            output = None if args.output == "-" else (args.output or args.input)
            dump(packet, output)
        elif args.command == "score":
            packet = score_packet(load(args.input))
            output = None if args.output == "-" else (args.output or args.input)
            dump(packet, output)
        elif args.command == "validate":
            errors = validate_packet(rank_hotspots(score_packet(load(args.input))))
            if errors:
                for error in errors:
                    print(f"ERROR: {error}")
                return 1
            print("OK: research packet is valid")
        elif args.command == "render":
            text = render(score_packet(load(args.input)))
            if args.output:
                Path(args.output).write_text(text, encoding="utf-8")
            else:
                print(text, end="")
        return 0
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
