---
name: cumcm-env-doctor
description: "检查 CUMCM 竞赛工作区的 Python 环境、依赖、系统工具与 Skill 可加载性。启动竞赛流程或排查环境缺项时使用。"
---

# CUMCM 环境自检

先建立隔离环境，再运行确定性检查。系统工具只检测和建议；未经用户确认不得安装、修改 MCP 配置或提升权限。

## 1. 锁定路径

确认：

- 用户竞赛工作区绝对路径；
- 本 Skill 包根目录；
- 题面与附件均在竞赛工作区 `input/`，且保持只读。

不要在 Skill 包目录中创建竞赛工作区，也不要把报告写到 `input/`。

## 2. 建立 uv 环境

检查 `uv --version`。缺少 uv 时，先向用户展示官方安装命令并获得确认：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

在竞赛工作区执行：

```bash
uv venv
```

已有 `.venv` 时复用，不删除或重建。uv 不可用且用户不安装时，降级为 `python -m venv .venv`，并在报告标记 `DEGRADED`。

## 3. 检查宿主联网通路

宿主 agent 亲自做轻量探测，不由 Python 脚本猜测：

1. 尝试用 WebSearch/WebFetch 读取 CUMCM 官网规则页；
2. 枚举已配置的搜索类 MCP，并对可用通路做无敏感信息的只读查询；
3. 只记录通路名称，不记录 Token、Cookie 或配置内容。

把成功通路用 `--network-channel` 传给脚本，例如：

```bash
uv run python <skill-pack>/skills/cumcm-env-doctor/scripts/check_env.py \
  --workspace . \
  --skill-pack-root <skill-pack> \
  --network-channel WebSearch
```

没有成功通路时省略参数。报告会把文献核验与赛制复核标记为 `DEGRADED`，但不阻塞本地建模。

## 4. 生成报告

脚本固定在竞赛工作区根写入：

- `env_report.json`：机器可读、供 hub 判门禁；
- `env_report.md`：中文摘要、缺项与安装建议。

输出路径不可配置，避免路径逃逸。完整检查项与降级方式见 [环境分层要求](references/env-requirements.md)。

## 5. 判定

- Tier 0 任一 `MISS`：脚本退出 1，`overall_status=BLOCKED`；hub 不得继续正式分析。
- Tier 0 全部 `OK`：脚本退出 0。
- Tier 1 `MISS`：按题型需要再用 `uv add` 安装，不阻塞。
- Tier 2 `DEGRADED`：显著告警并使用报告中的降级方式，不阻塞。
- 联网 `DEGRADED`：参考文献与当届规则改为人工核对，不阻塞。

安装任何缺失依赖后重新运行脚本，禁止手工把报告状态改为 `OK`。

## 6. Hub 交接

返回报告路径、overall 状态、Tier 0 缺项、Tier 1 候选项、Tier 2 降级项和联网通路。只有 Tier 0 全绿时才允许 hub 进入 startup lock。
