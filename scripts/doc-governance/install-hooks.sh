#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .githooks
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

echo "[doc-governance] .githooks/pre-commit 훅이 활성화되었습니다."
echo "[doc-governance] 파일 생성/수정 커밋 시 문서 검증이 실행됩니다."
