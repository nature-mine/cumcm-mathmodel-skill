# CUMCM MathModel Skill

面向 CUMCM 国赛的中文端到端 Skill 包，兼容 Codex 与 Claude Code 两种**二选一的单宿主**
部署方式。

状态：已发布，维护期。

本包定位为建模辅助、证据治理与质量门禁，不是“全自动出赛论文”工具。核心建模与分析、
路线确认、最终图件和提交决定仍由参赛队负责；使用 AI 时必须遵守当届规则并完成披露。

## 快速开始（3 步）

前置条件：Node.js（含 `npx`），以及能启动 Codex 或 Claude Code 之一。Python 环境由流程
第一步 `$cumcm-env-doctor` 自检，安装阶段无需准备。

每个竞赛项目只选一个宿主（Codex 或 Claude Code），不同时部署两套角色定义，也不中途换宿主。

```bash
# 1. 克隆本包（任意位置，只需一次）
git clone https://github.com/nature-mine/cumcm-mathmodel-skill.git

# 2. 在你的竞赛项目根目录执行一键安装（claude 或 codex 二选一）
mkdir my-contest && cd my-contest
bash /path/to/cumcm-mathmodel-skill/install.sh claude
```

`install.sh` 会自动完成：安装 7 个 Skill（`--copy`，安装结果不依赖 clone 目录的后续位置）、
部署所选宿主的角色定义与 workflow、创建 `input/` 与 `data/`、执行安装验收，并在末尾打印
第 3 步要用的启动提示语。

第 3 步：把题面 PDF 与官方附件放进 `input/`（只读；清洗、修复等派生数据只写 `data/`，
不得覆盖官方文件）；关闭安装前已打开的旧宿主会话，在竞赛项目根新开所选宿主会话，粘贴
`install.sh` 末尾打印的启动提示语。

启动提示语会加载 `$cumcm-hub`；宿主能力探测是 hub 的固定启动门禁。Codex 用户还需确认
`codex features list` 中 `multi_agent` 为 `stable true`。不使用脚本时的手动安装步骤见
[手动安装（备选）](#手动安装备选)。

### 让 Agent 帮你安装

不想手动执行命令，可以直接在竞赛项目根目录打开 Codex 或 Claude Code 会话，把下面这段话
复制给它（把仓库地址换成实际地址，`claude` 按所选宿主换成 `codex`）：

> 请帮我安装 CUMCM MathModel Skill 包：把
> `https://github.com/nature-mine/cumcm-mathmodel-skill` 克隆到当前目录之外的任意位置，
> 然后在当前目录执行 `bash <克隆路径>/install.sh claude`。确认输出列出 7 个 `cumcm-*`
> Skill 后，把脚本末尾打印的启动提示语原样转述给我。不要修改克隆下来的仓库内容，也不要
> 现在就启动建模流程。

安装完成后仍需自己完成第 3 步：放入题面、**新开会话**（Skill 与角色清单只在新会话中加载）、
粘贴启动提示语。

### 接下来会发生什么

`$cumcm-env-doctor` 先生成 `env_report.md` 与 `env_report.json`；随后 hub 发起 startup lock
六问，必须由用户补齐题号、输入、交付物和规则等约束。模型路线确认是人工决策点，除非用户
明确选择“全权委托”，否则不会代选。完整流程依次为：环境自检 → startup lock → 读题、数据
剖析与分型 → 拆解 → 模型路线确认 → 契约派发循环 → 阶段推进与返工传播 → 最终评审与提交门禁。
startup lock 会先初读输入以识别题面、附件和显式要求；后续“读题、数据剖析与分型”才是正式
分析阶段。

## Skill 索引

- [`cumcm-hub`](skills/cumcm-hub/SKILL.md)：编排八步流程、任务契约、阶段验收与返工闭环。
- [`cumcm-env-doctor`](skills/cumcm-env-doctor/SKILL.md)：检查 Python 环境、依赖、系统工具与 Skill 可加载性。
- [`cumcm-modeling`](skills/cumcm-modeling/SKILL.md)：建立模型假设、符号、推导、验证方案与实现交接。
- [`cumcm-coding`](skills/cumcm-coding/SKILL.md)：实现模型计算、结果落盘、数据图、运行记录与复现验证。
- [`cumcm-diagram`](skills/cumcm-diagram/SKILL.md)：路由数据图、精确结构图与概念图并维护图件登记。
- [`cumcm-writing`](skills/cumcm-writing/SKILL.md)：依据冻结证据撰写中文论文、组织附录与 AI 披露并导出 DOCX，随附可再生成的 [Markdown](skills/cumcm-writing/templates/paper-template.md)/[DOCX](skills/cumcm-writing/templates/paper-template.docx) 模板。
- [`cumcm-review`](skills/cumcm-review/SKILL.md)：对建模件、代码件和论文件执行分步检查与最终独立评审。

## 手动安装（备选）

`install.sh` 内部即以下步骤；需要自定义时可手动执行。将 `CUMCM_SKILL_PACK` 改为本包的
绝对路径，先确认 Skills CLI 能发现全部 Skill：

```bash
CUMCM_SKILL_PACK=/absolute/path/to/cumcm-mathmodel-skill
npx skills add "$CUMCM_SKILL_PACK" --list
```

方案 A：只用 Codex。在目标竞赛项目根执行：

```bash
npx skills add "$CUMCM_SKILL_PACK" \
  --agent codex \
  --skill '*' \
  --yes \
  --copy
mkdir -p .codex/agents
cp "$CUMCM_SKILL_PACK"/codex/agents/*.toml .codex/agents/
npx skills list --agent codex --json
codex features list
```

方案 B：只用 Claude Code。在目标竞赛项目根执行：

```bash
npx skills add "$CUMCM_SKILL_PACK" \
  --agent claude-code \
  --skill '*' \
  --yes \
  --copy
mkdir -p .claude/agents .claude/workflows
cp "$CUMCM_SKILL_PACK"/claude/agents/*.md .claude/agents/
cp "$CUMCM_SKILL_PACK"/claude/workflows/cumcm-contest.md .claude/workflows/
npx skills list --agent claude-code --json
```

随后创建 `input/`、放入题面与附件，并在新宿主会话中发送对应启动提示语。

Codex 启动提示语：

> 加载 `$cumcm-hub`，以当前目录作为竞赛工作区，按八步主流程执行。启动时先探测并记录 Codex 的 subagent 能力，然后调用 `$cumcm-env-doctor` 做环境自检并进行 startup lock 六问;任何信息缺失按 `stop_and_report` 停下，不得猜测。
> 能力可用时按 `.codex/agents/*.toml` 使用隔离角色派发，最终三席 reviewer 同时执行；若宿主有能力但角色、功能开关、只读门禁或并发条件未就绪，必须 `blocked`，不得顺序降级。

Claude Code 启动提示语：

> 加载 `$cumcm-hub`，以当前目录作为竞赛工作区，按 `.claude/workflows/cumcm-contest.md` 执行。先做环境自检和 startup lock；任何信息缺失按 stop-and-report 停下。

两条提示语都会加载 hub；宿主能力探测是 hub 的固定启动门禁。Claude Code 版保持 workflow
中的标准入口，由 workflow 与 hub 展开能力探测细节。

## 宿主部署与分派规则

### 安装边界

`skills add` 只安装 `skills/` 下的 7 个 Skill，不会部署包顶层的宿主适配文件。各 Skill 的
`agents/openai.yaml` 只是展示与调用元数据；必须根据所选宿主显式复制 `codex/agents/*.toml`，
或复制 `claude/agents/*.md` 与 `claude/workflows/cumcm-contest.md`（`install.sh` 已代为完成）。
`--copy` 使安装结果不依赖源 checkout 的后续位置。

Codex 的 Skill 安装目录为目标项目 `.agents/skills/`，四个 TOML 是项目级 custom agent
定义。Claude Code 使用四个独立 subagent 定义和八步 workflow。安装后须新开宿主会话，使
Skill 与角色清单重新加载；Codex 不使用 `claude/`，Claude Code 不使用 `codex/`。

### 子代理能力门禁

支持干净或最小上下文派发时，必须使用真正的 modeler、coder、writer、reviewer 子代理。
Codex 当前工具支持时使用 `fork_turns="none"` 或等价选项，只发送任务契约与声明输入。
reviewer 必须只读：Codex 定义采用只读沙箱、禁止审批和 Web Search；Claude Code reviewer
只开放 `Read/Grep/Glob`。

最终评审先冻结同一份 artifact manifest，再同时启动三个彼此隔离的只读 reviewer thread。
三席只返回消息，hub 等全部结束后才写报告与汇总，避免共享工作区泄漏先返回席位的意见。

只有确认宿主版本本身不提供 subagent 功能时，才允许顺序兜底。所有评审必须标注
`self-review, 独立性受限`，汇总写 `fallback_reason: subagent_unavailable`，且不得把 A/B/C
顺序复评称作三席盲评。宿主有能力但角色未部署、功能被配置禁用、限权未生效或并发不足时
必须 `blocked`，不得降级。

Codex custom agent 机制依据当前
[Codex Subagents 官方文档](https://learn.chatgpt.com/docs/agent-configuration/subagents)。

### 安装后自检

`npx skills list --agent <codex|claude-code> --json` 应返回 7 个项目级 Skill；看到 Skill 索引
中的 7 个名称即表示安装成功。角色文件缺失、能力被禁用或限权未生效不属于“无子代理环境”，
必须修复后重试。发送启动提示语后，hub 会调用已安装的 `cumcm-env-doctor/scripts/check_env.py`，
用户无需手动拼装脚本路径；只有报告中的 Skill 包检查和 Tier 0 全部为 `OK` 才进入 startup
lock。Tier 1/2 缺项按报告安装或降级，不代表安装失败。

## 开发验证

```bash
uv run pytest -q
uv run python scripts/validate_pack.py
uv run ruff check
```

`tests/` 与包顶层 `scripts/` 是包质量工具链，不随 `skills add` 安装；`skills/*/scripts/` 是
对应 Skill 的运行时资产，会随 Skill 安装。

内置 DOCX 模板使用一个仅含 `paper/paper.md` 的空竞赛工作区生成；支撑材料清单留在临时目录，
不会写入模板目录。需要重建二进制模板时，在包根执行：

```bash
TEMPLATE_WORKSPACE="$(mktemp -d)"
mkdir -p "$TEMPLATE_WORKSPACE"/{paper,input,data,code,support}
cp skills/cumcm-writing/templates/paper-template.md "$TEMPLATE_WORKSPACE/paper/paper.md"
uv run python skills/cumcm-writing/scripts/docx_export.py \
  --workspace "$TEMPLATE_WORKSPACE" \
  --source paper/paper.md \
  --output paper/paper-template.docx
cp "$TEMPLATE_WORKSPACE/paper/paper-template.docx" \
  skills/cumcm-writing/templates/paper-template.docx
```

`tests/test_paper_template.py` 会按相同 fixture 布局重新生成，并与仓库内 DOCX 做字节级比较。
