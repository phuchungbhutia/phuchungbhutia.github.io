---
title: "Configuring OpenCode with FreeLLMAPI, Image Generation, and Clean Plugins on Manjaro Linux"
description: "Route OpenCode through FreeLLMAPI, configure direct image providers, and manage plugins on Manjaro."
date: 2026-11-28 10:00:00 +0000
categories: [Linux, AI Tooling, Automation]
tags: ["opencode", "freellmapi", "openrouter", "google-ai-studio", "manjaro", "zsh", "mcp"]
---

# Configuring OpenCode with FreeLLMAPI, Image Generation, and Clean Plugins on Manjaro Linux

Running a local coding agent like **OpenCode** on Manjaro Linux with **Zsh** works best when text routing stays unified through a local gateway while specialized tasks use dedicated providers. This setup routes default chat through **FreeLLMAPI** while configuring direct image generation via **OpenRouter** or **Google AI Studio**. It also ensures persistent memory and session tooling remain stable by removing failing plugins.

## Adding a Direct Provider Alongside FreeLLMAPI for Image Generation

FreeLLMAPI handles chat and completion routing across free-tier backends, while OpenCode `v2.2.2+` supports `experimental.image_generate.model` when a direct image-capable provider is configured. You can authenticate via the `/connect` command to avoid hardcoding keys or declare them directly in the configuration file.

Keep `freellmapi/auto` as your primary model and set the experimental image model in `~/.config/opencode/opencode.json`. Validate the configuration after editing to ensure no syntax errors exist.

```bash
opencode auth list
opencode debug config
```

> Note: Using `/connect` stores credentials securely, whereas declaring them in JSON requires careful file permission management.

## Listing Free Image Models on OpenRouter with curl

Free image variants on OpenRouter appear on the API endpoint with model IDs ending in `:free`. You can filter these using `curl` combined with `jq` or Python if `jq` is not installed.

*   Use `jq` to filter model IDs ending in `:free`.
*   Use Python as an alternative parser for JSON responses.
*   Inspect specific model endpoints for parameter details.

```bash
curl -fsS -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  "https://openrouter.ai/api/v1/images/models" \
  | jq -r '.data[] | select(.id | endswith(":free")) | "\(.id)\t\(.name)"'
```

## Automated Media Setup Script

This Zsh script backs up the existing configuration, installs `ffmpeg` if missing, and preserves essential plugins like `opencode-mem` and `@dietrichgebert/ponytail`. It configures OpenRouter and Google AI Studio keys from environment variables and sets up optional MCP servers for Replicate or Fal.

```bash
cat << 'EOF' > ~/setup_opencode_media.sh
#!/usr/bin/env zsh
set -euo pipefail

CONFIG_DIR="$HOME/.config/opencode"
CONFIG_FILE="$CONFIG_DIR/opencode.json"
BACKUP_FILE="$CONFIG_DIR/opencode.json.bak.$(date +%Y%m%d_%H%M%S)"
VIDEO_HELPER="$HOME/render_video_ffmpeg.sh"

mkdir -p "$CONFIG_DIR"

if [[ -f "$CONFIG_FILE" ]]; then
  cp "$CONFIG_FILE" "$BACKUP_FILE"
  echo "Backed up existing config to: $BACKUP_FILE"
fi

IMAGE_MODEL="${OPENCODE_IMAGE_MODEL:-google/imagen-3.0-generate-002}"
OPENROUTER_KEY="${OPENROUTER_API_KEY:-}"
GOOGLE_KEY="${GOOGLE_GENERATIVE_AI_API_KEY:-${GEMINI_API_KEY:-${GOOGLE_API_KEY:-}}}"
REPLICATE_KEY="${REPLICATE_API_TOKEN:-}"
FAL_KEY_VAL="${FAL_KEY:-}"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Installing ffmpeg via pacman..."
  sudo pacman -S --needed --noconfirm ffmpeg
fi

python3 - "$CONFIG_FILE" "$IMAGE_MODEL" "$OPENROUTER_KEY" "$GOOGLE_KEY" "$REPLICATE_KEY" "$FAL_KEY_VAL" << 'PYEOF'
import json, os, sys

cfg_path, img_model, or_key, google_key, rep_key, fal_key = sys.argv[1:7]

data = {}
if os.path.exists(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

data["$schema"] = "https://opencode.ai/config.json"
data.setdefault("model", "freellmapi/auto")

plugins = data.get("plugin", [])
if not isinstance(plugins, list):
    plugins = []
for p in ["opencode-mem", "@dietrichgebert/ponytail"]:
    if p not in plugins:
        plugins.append(p)
data["plugin"] = plugins

providers = data.setdefault("provider", {})
providers.setdefault("freellmapi", {
    "npm": "@ai-sdk/openai-compatible",
    "name": "FreeLLMAPI (Local)",
    "options": {
        "baseURL": "http://127.0.0.1:3001/v1",
        "apiKey": "freellmapi-201323df876722c005c68ca5f836ad6cae55620ee323772c"
    },
    "models": {
        "auto": {
            "name": "Auto Router",
            "limit": {"context": 1048576, "output": 65536}
        }
    }
})

if or_key:
    providers["openrouter"] = {
        "options": {"apiKey": or_key}
    }

if google_key:
    providers["google"] = {
        "options": {"apiKey": google_key}
    }

exp = data.setdefault("experimental", {})
exp["image_generate"] = {"model": img_model}

mcp = data.setdefault("mcp", {})
if rep_key:
    mcp["replicate"] = {
        "type": "local",
        "command": ["npx", "-y", "mcp-replicate"],
        "environment": {"REPLICATE_API_TOKEN": rep_key},
        "enabled": True
    }
if fal_key:
    mcp["fal"] = {
        "type": "local",
        "command": ["npx", "-y", "fal-mcp-server"],
        "environment": {"FAL_KEY": fal_key},
        "enabled": True
    }

with open(cfg_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print("Updated:", cfg_path)
PYEOF

echo "Validating OpenCode configuration..."
opencode debug config >/dev/null
echo "Done. Setup complete."
EOF
chmod +x ~/setup_opencode_media.sh
```

Run the setup script and export necessary environment variables before execution. You can switch image models or add plugins directly via command line tools after the initial setup.

```bash
export GOOGLE_GENERATIVE_AI_API_KEY="AIzaSy_YOUR_GOOGLE_AI_STUDIO_KEY"
export OPENROUTER_API_KEY="sk-or-v1-YOUR_OPENROUTER_KEY"
~/setup_opencode_media.sh
```

## Removing Failing Plugins and Running a Stack Health Check

Remove `supermemory` and `opencode-litellm` from global and local configuration files to prevent startup errors. Clear stale plugin caches to ensure a clean state for remaining tools.

*   Identify and remove bad plugins from JSON configurations.
*   Clear node modules cache for OpenCode.
*   Verify FreeLLMAPI gateway status and plugin presence.

```bash
python3 - << 'PYEOF'
import json, os

paths = [
    os.path.expanduser("~/.config/opencode/opencode.json"),
    os.path.abspath("./opencode.json"),
]
bad_plugins = {"supermemory", "opencode-litellm", "opencode-plugin-litellm"}

for path in paths:
    if not os.path.exists(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False
    for key in ("plugins", "plugin"):
        if isinstance(data.get(key), list):
            filtered = [
                p for p in data[key]
                if not any(b in (p if isinstance(p, str) else str(p)) for b in bad_plugins)
            ]
            if filtered != data[key]:
                data[key] = filtered
                changed = True

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"Cleaned: {path}")
PYEOF

rm -rf ~/.cache/opencode/node_modules ~/.config/opencode/node_modules
```

Verify the stack health by checking Docker containers, plugin lists, and recent logs for errors. This ensures the local gateway and essential plugins are operational.

```bash
curl -fsS http://127.0.0.1:3001/v1/models \
  -H "Authorization: Bearer freellmapi-201323df876722c005c68ca5f836ad6cae55620ee323772c" \
  | head -c 300 && echo ""

opencode plugin list
opencode debug config >/dev/null && echo "Config JSON: VALID"
```

## Summary

*   Route chat through FreeLLMAPI while using direct providers for image generation.
*   Automate configuration updates and plugin management with Zsh scripts.
*   Remove failing plugins and validate the stack to ensure stability.

## References

*   [OpenCode Documentation](https://opencode.ai)
*   [FreeLLMAPI GitHub](https://github.com/freellmapi/freellmapi)
*   [OpenRouter API Docs](https://openrouter.ai/docs)