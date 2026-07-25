#!/usr/bin/env bash
# 一键把本 Skill 包安装到一个竞赛项目(单宿主:codex 或 claude 二选一)。
# 用法:在竞赛项目根目录执行
#   bash /path/to/cumcm-mathmodel-skill/install.sh <codex|claude>
set -euo pipefail

PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOST="${1:-}"
TARGET_DIR="$(pwd)"

usage() {
  echo "用法: bash $0 <codex|claude>   # 在竞赛项目根目录执行"
  exit 1
}

case "$HOST" in
  codex) AGENT="codex" ;;
  claude) AGENT="claude-code" ;;
  *) usage ;;
esac

if [ "$TARGET_DIR" = "$PACK_DIR" ]; then
  echo "错误: 请在竞赛项目根目录执行本脚本,不要在 Skill 包目录内执行。" >&2
  exit 1
fi

if ! command -v npx >/dev/null 2>&1; then
  echo "错误: 未找到 npx,请先安装 Node.js。" >&2
  exit 1
fi

echo "==> 1/4 安装 7 个 Skill(宿主: $HOST)"
npx skills add "$PACK_DIR" --agent "$AGENT" --skill '*' --yes --copy

echo "==> 2/4 部署宿主角色定义"
if [ "$HOST" = "codex" ]; then
  mkdir -p .codex/agents
  cp "$PACK_DIR"/codex/agents/*.toml .codex/agents/
else
  mkdir -p .claude/agents .claude/workflows
  cp "$PACK_DIR"/claude/agents/*.md .claude/agents/
  cp "$PACK_DIR"/claude/workflows/cumcm-contest.md .claude/workflows/
fi

echo "==> 3/4 准备工作区目录(input/ 放题面与官方附件,只读;派生数据写 data/)"
mkdir -p input data

echo "==> 4/4 验收:以下列表应包含 7 个 cumcm-* Skill"
npx skills list --agent "$AGENT" --json
if [ "$HOST" = "codex" ]; then
  echo "请另行确认: codex features list 中 multi_agent 为 stable true。"
fi

echo
echo "安装完成。接下来:"
echo "  1. 把题面 PDF 与官方附件放入 input/"
echo "  2. 关闭旧的 $HOST 会话,在本目录新开会话"
echo "  3. 粘贴以下启动提示语:"
echo
if [ "$HOST" = "codex" ]; then
  cat <<'PROMPT'
加载 $cumcm-hub,以当前目录作为竞赛工作区,按八步主流程执行。启动时先探测并记录 Codex 的 subagent 能力,然后调用 $cumcm-env-doctor 做环境自检并进行 startup lock 六问;任何信息缺失按 stop_and_report 停下,不得猜测。
能力可用时按 .codex/agents/*.toml 使用隔离角色派发,最终三席 reviewer 同时执行;若宿主有能力但角色、功能开关、只读门禁或并发条件未就绪,必须 blocked,不得顺序降级。
PROMPT
else
  cat <<'PROMPT'
加载 $cumcm-hub,以当前目录作为竞赛工作区,按 .claude/workflows/cumcm-contest.md 执行。先做环境自检和 startup lock;任何信息缺失按 stop-and-report 停下。
PROMPT
fi
