#!/usr/bin/env bash
set -euo pipefail

_CURRENT_DIR=$(dirname "${BASH_SOURCE[0]}")

# Fetch scripts Root
SCRIPTS_CI_DIR="$(cd "${_CURRENT_DIR}"/.. && pwd)"
export SCRIPTS_CI_DIR

# Fetch Git Root
GIT_ROOT=$(git rev-parse --show-toplevel)
export GIT_ROOT

RED='\033[0;31m'
NC='\033[0m'
CYAN='\033[0;36m'
GREEN='\033[1;32m'
GREY='\033[1;36m'

# Prepare log file
HADOLINT_ERROR="${HOME}/.cache/hadolint/log.txt"
mkdir -p $(dirname $HADOLINT_ERROR)
