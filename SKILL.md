---
name: xinran-interview-planner
description: 为“昕然有约”策划人物采访。输入嘉宾姓名、主页或少量背景后，研究身份与公开资料，连接观众正在面对的问题和近期热点，筛选适合该嘉宾的教育家庭、事业财富、女性成长、圈层人生、AI 或机器人话题，生成访前研究包、选题评分、问题追问树、传播切片和主持人手卡。用于嘉宾研究、采访选题、热点分析、采访提纲、邀约判断、访前策划和稿件审查。最低输入可以只有嘉宾姓名。
---

# 昕然有约采访策划

目标：带着观众正在面对的问题，去见真正有经历、有结果的人，问出有参考价值的答案。

## 先调用工具

脚本路径均相对于本 Skill：

```bash
python scripts/xinran_interview.py --help
python scripts/xinran_interview.py init --guest "嘉宾姓名" --identity "可选身份"
python scripts/xinran_interview.py queries --guest "嘉宾姓名" --identity "可选身份"
python scripts/xinran_interview.py topics --tag "自媒体" --keyword "AI"
python scripts/xinran_interview.py score --input research.json
python scripts/xinran_interview.py validate --input research.json
python scripts/xinran_interview.py render --input research.json --output interview-plan.md
```

先运行 `init` 创建研究包，再运行 `queries` 生成检索计划，并用 `topics` 从内置话题库筛选候选。用可用的搜索、浏览器或用户资料完成研究，把来源、事实和候选话题写回研究包。运行 `score`、`validate`，最后运行 `render` 生成稳定骨架，再由 AI 补齐有判断力的内容。

用户问“怎么用”“支持什么”“帮助”时，先运行 `python scripts/xinran_interview.py help`，根据输出回答。

## AI 负责的部分

- 同名消歧与来源核验。
- 判断观众真实问题，而非只追热搜。
- 找到只有该嘉宾能回答的故事、经历、结果和代价。
- 为每位嘉宾独立设计开场；禁止机械复用统一模板。
- 前 10 秒先呈现具体矛盾，不先介绍履历；随后用嘉宾身份建立答案可信度。
- 将抽象回答追到场景、选择、证据、代价、边界和普通人意义。
- 根据平台与嘉宾调整标题、切片和节奏。

## 按需读取

- 开始策划前读取 [references/account-positioning.md](references/account-positioning.md)。
- 给候选话题打分或处理敏感议题时读取 [references/editorial-rubric.md](references/editorial-rubric.md)。
- 不要把 references 全部复述进输出。

## 必守边界

- AI、机器人是可选方向，不是强制入口。
- 区分 `已证实`、`嘉宾自述`、`媒体报道`、`待核实`、`策划假设`。
- 热点注明来源和日期；无法实时检索时明确说明。
- 不神化名校、财富、母职、圈层或成功。
- 对儿童、婚姻、健康、疗愈、产品安全、争议和法律问题保持克制；证据不足时改成问题。
- 不模仿真实主持人的身份、口头禅或私人表达。

默认输出一页结论、嘉宾画像、观众问题、热点雷达、话题评分、三个主选题、采访结构、追问树、传播包装和昕然手卡。发布组合默认规划 1 条主访谈、2—3 条具体问题切片、1 条昕然采访手记。工具生成结构，AI 生成判断。
