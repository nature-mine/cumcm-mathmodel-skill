# AGENT_INSTALL — 写给 Coding Agent 的安装说明

本文件面向 Coding Agent（Codex、Claude Code 等）：用户会要求你按本文把
CUMCM MathModel Skill 包安装到当前项目。按顺序执行，不要跳步；给人看的安装
说明见 [README](README.md)。

## 0. 确认输入

开始前从用户消息中确认两件事，缺哪个就先问用户，不要猜：

1. 包来源：GitHub 仓库地址（默认
   `https://github.com/nature-mine/cumcm-mathmodel-skill`）或本地已克隆路径。
2. 目标 Agent：`claude`（Claude Code）或 `codex`（Codex），即用户参赛要用的那一个。
   每个竞赛项目只部署一套角色定义，不要两套都装。

当前工作目录应是用户的竞赛项目根目录。若当前目录就是本包（存在
`skills/cumcm-hub/`），停下并请用户切换到竞赛项目目录后再执行。

## 1. 获取包

用户已给出本地克隆路径则跳过本步。否则把仓库克隆到竞赛项目目录**之外**
（例如上一级目录），不要克隆进竞赛项目内：

```bash
git clone https://github.com/nature-mine/cumcm-mathmodel-skill.git ../cumcm-mathmodel-skill
```

## 2. 安装

优先使用一键脚本（bash 脚本；Windows 环境在 WSL 或 Git Bash 中执行）。命令中的
`../cumcm-mathmodel-skill` 路径按实际克隆位置替换。`<claude|codex>` 填用户所选：

```bash
bash ../cumcm-mathmodel-skill/install.sh <claude|codex>
```

脚本依次完成：用 `npx skills add --copy` 安装 7 个 Skill 到所选 Agent 的项目级
Skill 目录（codex 为 `.agents/skills/`，claude 为 `.claude/skills/`）；部署角色定义
（codex 为 `.codex/agents/*.toml`，claude 为 `.claude/agents/*.md` 与
`.claude/workflows/cumcm-contest.md`）；创建 `input/` 与 `data/`；打印验收结果与
启动提示语。

一键脚本无法使用或需要自定义时，仍在 bash 环境中按
[README 的“手动安装（备选）”](README.md#手动安装备选)逐条执行等价命令。

## 3. 验收

以下各项全部满足才算安装成功；有不满足项时修复后重试，不要略过：

1. `npx skills list --agent <codex|claude-code> --json` 列出 7 个 `scope` 为
   `project` 的 Skill：`cumcm-coding`、`cumcm-diagram`、`cumcm-env-doctor`、
   `cumcm-hub`、`cumcm-modeling`、`cumcm-review`、`cumcm-writing`。
2. 角色定义就位：codex 为 `.codex/agents/` 下 4 个 TOML；claude 为
   `.claude/agents/` 下 4 个 `.md` 加 `.claude/workflows/cumcm-contest.md`。
3. `input/` 与 `data/` 目录存在。
4. 仅 codex：在终端运行 `codex features list`，确认输出中 `multi_agent` 一行为
   `stable true`。不满足时如实报告，不要伪造结果。

## 4. 完成后必须做的事

1. 把对应的启动提示语（见文末）原样转述给用户，并说明后续动作：把题面 PDF 与
   官方附件放入 `input/`（只读；派生数据只写 `data/`），然后**新开**一个所选
   Agent 的会话粘贴提示语——Skill 与角色清单只在新会话中加载，当前会话看不到。
2. 到此为止。不要在当前会话中替用户启动建模流程，也不要替用户回答 startup lock。

## 边界约定

- 不得修改克隆下来的包内容，也不要把题面、数据放进包目录。
- 只部署用户所选的一套角色定义；`claude/` 与 `codex/` 不混用。
- 安装失败时报告真实错误输出，不得伪造验收结果。

## 启动提示语

Codex（`install.sh codex` 末尾也会打印同一段）：

> 加载 `$cumcm-hub`，以当前目录作为竞赛工作区，按八步主流程执行。启动时先探测并记录 Codex 的 subagent 能力，然后调用 `$cumcm-env-doctor` 做环境自检并进行 startup lock 六问；任何信息缺失按 `stop_and_report` 停下，不得猜测。
> 能力可用时按 `.codex/agents/*.toml` 使用隔离角色派发，最终三席 reviewer 同时执行；若宿主有能力但角色、功能开关、只读门禁或并发条件未就绪，必须 `blocked`，不得顺序降级。

Claude Code（`install.sh claude` 末尾也会打印同一段）：

> 加载 `$cumcm-hub`，以当前目录作为竞赛工作区，按 `.claude/workflows/cumcm-contest.md` 执行。先做环境自检和 startup lock；任何信息缺失按 stop-and-report 停下。
