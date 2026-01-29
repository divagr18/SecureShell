# Configuration

SecureShell supports configuration via code (`SecureShellConfig`) or `secureshell.yaml`.

## File Configuration (`secureshell.yaml`)

You can define these in a `secureshell.yaml` file in your root directory. Use **snake_case** for keys.

```yaml
debug_mode: true
provider: "openai"

allowlist:
  - "ls"
  - "echo"

blocklist:
  - "rm"
  - "netcat"

default_timeout_seconds: 60
```


## Supported Options

The following options are supported in both TypeScript and Python SDKs.

### Core Settings

| Option | Type | Description |
|--------|------|-------------|
| `debug_mode` | boolean | Enable verbose logging. (TS: `debugMode`) |
| `provider` | string | Default LLM provider (e.g., `openai`). |
| `os_info` | string | Override OS detection (e.g., "Windows 10"). (TS: `osInfo`) |

### Security Rules

| Option | Type | Description |
|--------|------|-------------|
| `allowlist` | string[] | List of command types to ALWAYS allow (bypasses gatekeeper). |
| `blocklist` | string[] | List of command types to ALWAYS block. |

### Audit & Execution

| Option | Default | Description |
|--------|---------|-------------|
| `default_timeout_seconds` | 300 | Max time for command execution. (TS: `defaultTimeoutSeconds`) |
| `max_output_bytes` | 1MB | Max stdout capture size. (TS: `maxOutputBytes`) |
| `audit_log_path` | `audit.jsonl` | Path to audit log file. (TS: `auditLogPath`) |
| `audit_queue_size` | 1000 | Max audit events to buffer. (TS: `auditQueueSize`) |