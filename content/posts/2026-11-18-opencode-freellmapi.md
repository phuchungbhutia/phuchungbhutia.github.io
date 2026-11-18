---
title: "Building a Local AI Gateway with FreeLLMAPI and OpenCode on Manjaro Linux"
description: "A technical guide to unifying free-tier AI API providers using a self-hosted FreeLLMAPI Docker proxy and OpenCode CLI."
date: 2026-11-18 12:00:00 +0000
categories: [DevOps, Artificial Intelligence, Linux]
tags: [freellmapi, opencode, docker, manjaro, ai-gateway]
---

# Building a Local AI Gateway with FreeLLMAPI and OpenCode on Manjaro Linux

Managing multiple AI provider keys across different development tools quickly becomes cumbersome. This guide details how to build a centralized, self-hosted local routing proxy using FreeLLMAPI in Docker on Manjaro Linux. We integrate this gateway seamlessly with the OpenCode CLI assistant, covering architecture, common errors, and exact solutions.

## Architecture Overview

The system architecture relies on three primary layers to route requests securely:

*   **The Gateway Layer:** FreeLLMAPI runs locally in Docker on port `3001`, managing upstream API keys securely in an encrypted local database.
*   **The Shell Environment Layer:** Zsh shell environment variables (`FREELLMAPI_KEY`) act as a secure bridge for authentication.
*   **The Client Layer:** OpenCode is configured via `~/.config/opencode/opencode.json` to route all completion requests directly through the local proxy.

## Step-by-Step Implementation and Troubleshooting

### Repository Cloning and Path Errors

Attempting to run a quick setup script or navigating directly into a non-existent directory throws a directory error. Additionally, fetching an online install script may fail due to DNS resolution issues.

Resolve this by manually cloning the official repository and setting up the local configuration files:

```bash
git clone https://github.com/tashfeenahmed/freellmapi.git ~/freellmapi
cd ~/freellmapi
printf "ENCRYPTION_KEY=%s\nPORT=3001\n" "$(openssl rand -hex 32)" > .env
```

### Docker Socket Permissions

When executing Docker commands or starting Docker Compose, the daemon may reject the connection with a permission denied error. 

Resolve this by refreshing the active shell group memberships without requiring a system reboot:

```bash
newgrp docker
```

> **Note:** Verify the fix by running `docker info >/dev/null && echo "Docker is ready"`. If the issue persists, ensure your user is added to the Docker group permanently using `sudo usermod -aG docker $USER`.

### Container Management and Logs

Checking container status or startup logs prematurely results in missing container errors. The Docker daemon cannot find a container that has not been started.

Ensure you are inside the repository directory where the Docker Compose file resides, then start the stack:

```bash
cd ~/freellmapi
docker compose up -d
```

Verify active containers using `docker ps`.

### OpenCode Authentication and Key Resolution

Even though `FREELLMAPI_KEY` is verified in the Zsh environment, OpenCode may throw an `invalid api key` error during model execution. Background processes and non-login shells do not always inherit unexported session variables.

First, test the gateway directly via `curl` to confirm the local proxy accepts the key outside OpenCode:

```bash
curl -s http://127.0.0.1:3001/v1/chat/completions \
  -H "Authorization: Bearer $FREELLMAPI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"auto","messages":[{"role":"user","content":"Say hi"}]}'
```

A successful output returns a JSON payload with an `execution_id` and routed model details. 

Second, harden the OpenCode configuration to eliminate environment variable lookup issues. Explicitly provide the literal verified key inside `~/.config/opencode/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "freellmapi/auto",
  "provider": {
    "freellmapi": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "FreeLLMAPI (Local)",
      "options": {
        "baseURL": "http://127.0.0.1:3001/v1",
        "apiKey": "freellmapi-201323df876722c005c68ca5f836ad6cae55620ee323772c"
      },
      "models": {
        "auto": {
          "name": "Auto Router",
          "limit": { "context": 1048576, "output": 65536 }
        }
      }
    }
  }
}
```

## Summary

*   FreeLLMAPI provides a secure, local Docker-based gateway for managing multiple upstream AI provider keys.
*   Docker permission errors on Manjaro Linux are resolved efficiently using `newgrp docker` or modifying user groups.
*   Hardcoding the verified API key in `opencode.json` prevents shell environment inheritance failures in background processes.
*   This architecture creates a unified, maintainable routing stack for local AI development.

## References

*   [FreeLLMAPI GitHub Repository](https://github.com/tashfeenahmed/freellmapi)
*   [OpenCode Configuration Schema](https://opencode.ai/config.json)
*   [Docker Post-Installation Steps for Linux](https://docs.docker.com/engine/install/linux-postinstall/)