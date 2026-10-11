#!/usr/bin/env bash
# scripts/install_clis.sh
# Idempotent installer for all supported sandbox provider CLIs.
# Supports macOS (Darwin) arm64/x86_64 and Linux.

set -euo pipefail

DEST_BIN="${HOME}/.local/bin"
mkdir -p "${DEST_BIN}"
export PATH="${DEST_BIN}:${PATH}"

echo "=========================================================="
echo " Sandbox Benchmarking Suite - CLI Installer & Verifier   "
echo " Target directory: ${DEST_BIN}                            "
echo "=========================================================="

# 1. Blaxel CLI ('bl')
if command -v bl >/dev/null 2>&1; then
    echo "✓ Blaxel CLI already installed: $(command -v bl)"
else
    echo "-> Installing Blaxel CLI..."
    curl -fsSL https://blaxel.ai/install.sh | sh || true
fi

# 2. Modal CLI ('modal')
if command -v modal >/dev/null 2>&1; then
    echo "✓ Modal CLI already installed: $(command -v modal)"
else
    echo "-> Installing Modal CLI..."
    if command -v uv >/dev/null 2>&1; then
        uv tool install modal || curl -LsSf uvx.sh/modal/install.sh | sh
    else
        curl -LsSf uvx.sh/modal/install.sh | sh
    fi
fi

# 3. Databricks CLI ('databricks')
if command -v databricks >/dev/null 2>&1; then
    echo "✓ Databricks CLI already installed: $(command -v databricks)"
else
    echo "-> Installing Databricks CLI..."
    DATABRICKS_RUNTIME_VERSION=1 sh -c "$(curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh)" || true
    if [ -f "${HOME}/bin/databricks" ]; then
        ln -sf "${HOME}/bin/databricks" "${DEST_BIN}/databricks"
    fi
fi

# 4. Daytona CLI ('daytona')
if command -v daytona >/dev/null 2>&1; then
    echo "✓ Daytona CLI already installed: $(command -v daytona)"
else
    echo "-> Installing Daytona CLI..."
    ARCH="arm64"
    [ "$(uname -m)" = "x86_64" ] && ARCH="amd64"
    OS="darwin"
    [ "$(uname -s)" = "Linux" ] && OS="linux"
    curl -fsSL -o "${DEST_BIN}/daytona" "https://github.com/daytonaio/daytona/releases/download/v0.190.0/daytona-${OS}-${ARCH}" || true
    chmod +x "${DEST_BIN}/daytona" || true
fi

# 5. AWS CLI ('aws')
if command -v aws >/dev/null 2>&1; then
    echo "✓ AWS CLI already installed: $(command -v aws)"
else
    echo "-> Installing AWS CLI..."
    if command -v uv >/dev/null 2>&1; then
        uv tool install awscli || true
    fi
fi

# 6. E2B CLI ('e2b')
if command -v e2b >/dev/null 2>&1; then
    echo "✓ E2B CLI already installed: $(command -v e2b)"
else
    echo "-> Installing E2B CLI..."
    if command -v npm >/dev/null 2>&1; then
        npm install -g @e2b/cli || true
    elif command -v bun >/dev/null 2>&1; then
        bun install -g @e2b/cli || true
    fi
fi

# 7. GCP Agent Sandbox CLI ('agent-sandbox')
if command -v agent-sandbox >/dev/null 2>&1; then
    echo "✓ GCP agent-sandbox CLI already installed: $(command -v agent-sandbox)"
else
    echo "-> Install the external agent-sandbox CLI; see providers/gcp_vertex/client-reference.md."
fi

# 8. Alibaba Cloud CLI ('aliyun')
if command -v aliyun >/dev/null 2>&1; then
    echo "✓ Alibaba Cloud CLI already installed: $(command -v aliyun)"
else
    echo "-> Installing Alibaba Cloud CLI..."
    if command -v brew >/dev/null 2>&1; then
        brew install aliyun-cli || true
    fi
fi

echo ""
echo "=========================================================="
echo " Verification Report:                                     "
echo "=========================================================="
for cmd in bl modal databricks daytona aws e2b agent-sandbox gcloud uv aliyun; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "  [OK]   $cmd -> $(command -v "$cmd")"
    else
        echo "  [MISS] $cmd is not found in PATH"
    fi
done
echo "=========================================================="
