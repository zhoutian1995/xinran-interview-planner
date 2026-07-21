---
name: xinran-interview-planner
description: 为“昕然有约”发现热点并策划人物采访。主动研究当前公开信息，选出4个有证据的热点，解释每个热点为什么在此刻成立、来源与生命周期；每个热点展开5个普通人关心的具体采访话题，并为每个话题推荐适合嘉宾及匹配理由。也支持输入嘉宾姓名后反向匹配热点、生成访前研究包、追问树、传播切片和主持人手卡。用于热点选题、嘉宾推荐、采访策划、邀约判断和稿件审查。
---

# 昕然有约采访策划

目标：带着观众正在面对的问题，去见真正有经历、有结果的人，问出有参考价值的答案。

## 先调用工具

```bash
python scripts/xinran_interview.py --help
python scripts/xinran_interview.py init --guest "待定"
python scripts/xinran_interview.py rank-hotspots --input research.json
python scripts/xinran_interview.py topics --tag "自媒体" --keyword "AI"
python scripts/xinran_interview.py validate --input research.json
python scripts/xinran_interview.py render --input research.json --output interview-plan.md
```

默认先研究热点，不先等待嘉宾。用搜索或浏览器采集热点证据，写入 `hotspot_candidates`；运行 `rank-hotspots` 选出前4名。为每个热点生成恰好5个具体采访话题，每个话题包含推荐嘉宾、匹配理由和证据目标。用户已有嘉宾时，再用 `queries`、`topics` 反向匹配。

用户问帮助时运行 `python scripts/xinran_interview.py help`。

## AI 负责

- 核验热点来源、嘉宾身份和一手经历。
- 解释热点如何形成：发生了什么、谁在讨论、为何影响目标观众、热度处于什么阶段。
- 把热点翻译成普通人正在面对的具体选择，而非复述热搜。
- 为每位嘉宾独立设计开场；前10秒先出现具体矛盾，再用嘉宾身份建立可信度。
- 把回答追到场景、选择、证据、代价、边界和普通人意义。

## 按需读取

- 账号定位：[references/account-positioning.md](references/account-positioning.md)
- 热点定义与4×5规则：[references/hotspot-method.md](references/hotspot-method.md)
- 实时研究协议：[references/live-research.md](references/live-research.md)
- 选题评分与敏感边界：[references/editorial-rubric.md](references/editorial-rubric.md)

## 硬性输出

第一交付物固定为：4个热点；每个热点说明来源、成立理由、证据和生命周期；每个热点恰好5个采访话题；每个话题推荐嘉宾类型或具体人选并说明为什么适合。总计20个可执行采访话题。

用户确认嘉宾后，再输出访前策划、追问树、传播包装和昕然手卡。默认规划1条主访谈、2—3条具体问题切片、1条昕然采访手记。

## 边界

- 热点必须带来源和日期；无法实时检索时明确说明。
- AI、机器人是可选方向，不是强制入口。
- 区分 `已证实`、`嘉宾自述`、`媒体报道`、`待核实`、`策划假设`。
- 不神化名校、财富、母职、圈层或成功。
- 儿童、婚姻、健康、疗愈、产品安全、争议和法律问题证据不足时改成问题。
