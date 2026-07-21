# Xinran Interview Planner

“昕然有约”人物采访策划 Skill：输入嘉宾姓名，研究观众问题、人物经历与近期热点，生成可录制、可追问、可切片的访前方案。

> 有问题，昕然带你去见个朋友。

## 账号定位

“昕然有约”不是只做 AI 或机器人的垂类账号。昕然的角色是不同圈层的连接者：带着一二线城市年轻人和中产家庭正在面对的问题，去见真正有经历、有结果的人。

内容覆盖：

- 教育与家庭
- 事业与财富
- 女性与成长
- 圈层与人生
- 昕然个人内容
- AI 与机器人（按嘉宾真实关联选用）

## 为什么这个 Skill 不只是提示词

SKILL.md 只保存调用流程和硬边界。重复、确定性的工作交给 `scripts/xinran_interview.py`：

- 初始化结构化研究包
- 生成身份消歧和分主题检索式
- 计算候选话题六维评分
- 校验来源、事实标签和评分字段
- 渲染统一的 Markdown 策划骨架
- 提供 CLI 帮助

AI 只负责需要判断的部分：核验人物、理解观众问题、发现独特故事、设计独立开场、形成追问和传播策略。

## 安装

### Codex

```bash
git clone https://github.com/zhoutian1995/xinran-interview-planner.git ~/.codex/skills/xinran-interview-planner
```

### 通用 Agents Skills

```bash
git clone https://github.com/zhoutian1995/xinran-interview-planner.git ~/.agents/skills/xinran-interview-planner
```

## 最简用法

在支持 Skills 的 Agent 中输入：

```text
使用 $xinran-interview-planner。
嘉宾：杏仁
```

只提供姓名也能开始。若同名较多，补一个身份或主页：

```text
使用 $xinran-interview-planner 为昕然有约做访前策划。
嘉宾：喵小兔
身份：小红书博主
主页：<链接>
预计平台：小红书、视频号
```

## CLI 帮助

```bash
python scripts/xinran_interview.py --help
python scripts/xinran_interview.py help
```

## 推荐工作流

### 1. 初始化研究包

```bash
python scripts/xinran_interview.py init \
  --guest "嘉宾姓名" \
  --identity "身份线索" \
  --platform "小红书" \
  --platform "视频号" \
  --duration 30 \
  --output research.json
```

Windows PowerShell：

```powershell
python scripts/xinran_interview.py init `
  --guest "嘉宾姓名" `
  --identity "身份线索" `
  --platform "小红书" `
  --platform "视频号" `
  --duration 30 `
  --output research.json
```

### 2. 生成检索计划

```bash
python scripts/xinran_interview.py queries --guest "嘉宾姓名" --identity "身份线索"
```

可只研究指定内容主线：

```bash
python scripts/xinran_interview.py queries \
  --guest "嘉宾姓名" \
  --pillar education-family \
  --pillar ai-robotics
```

支持的 pillar：

| 参数 | 方向 |
|---|---|
| `education-family` | 教育与家庭 |
| `career-wealth` | 事业与财富 |
| `women-growth` | 女性与成长 |
| `circles-life` | 圈层与人生 |
| `xinran-personal` | 昕然个人内容 |
| `ai-robotics` | AI 与机器人 |

### 3. 填写研究结果

把公开资料写入 `research.json`：

- `sources`：标题、URL、发布日期、访问日期
- `facts`：事实标签、内容和来源引用
- `audience_questions`：观众正在面对的问题
- `topic_candidates`：候选话题、理由、风险和六维评分

事实标签只能使用：`已证实`、`嘉宾自述`、`媒体报道`、`待核实`、`策划假设`。

### 4. 评分

```bash
python scripts/xinran_interview.py score --input research.json
```

评分维度均为 1-5：

- `guest_fit`
- `audience_need`
- `timeliness`
- `depth`
- `distribution`
- `safety`

工具会自动计算总分并给出主选题、条件主选题、备选或删除建议。

### 5. 校验

```bash
python scripts/xinran_interview.py validate --input research.json
```

### 6. 生成策划骨架

```bash
python scripts/xinran_interview.py render --input research.json --output interview-plan.md
```

Agent 再基于该骨架完成独立开场、采访结构、追问树、标题切片和昕然主持人手卡。

## 每期输出

1. 一页结论
2. 身份核验与嘉宾画像
3. 观众问题与近期热点
4. 候选话题评分
5. 三个主选题与两个备选题
6. 针对该嘉宾的独立开场
7. 采访结构与追问树
8. 传播包装
9. 昕然主持人手卡

## 关键原则

- 每位嘉宾单独策划，不设置统一开场模板。
- AI 和机器人只在与嘉宾有真实连接时使用。
- 热点服务于人物和观众问题，不用热搜替代人物研究。
- 名校只是结果，重点追问问题、错误、选择和适用边界。
- 圈层只是入口，重点是人物真实经历和观众可参考的答案。

## 测试

```bash
python -m unittest scripts/test_xinran_interview.py -v
```

本工具只使用 Python 标准库，不需要额外安装依赖。
