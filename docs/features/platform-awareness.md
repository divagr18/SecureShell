# Platform Awareness

SecureShell automatically detects your operating system and ensures commands are platform-compatible. This prevents agents from running Unix commands on Windows or vice versa.

## Automatic OS Detection

SecureShell detects your OS at initialization:

```typescript
const shell = new SecureShell(); // Auto-detects Windows/macOS/Linux
console.log(shell.getOSInfo()); // "Windows 10", "macOS 14.1", etc.
```

No configuration needed - it just works.

## How It Helps

### Cross-Platform Command Blocking

**On Windows:**
```typescript
await shell.execute('ls -la', 'List files');
// ❌ DENY: "ls is a Unix command. Use 'dir' on Windows."
```

**On Linux/macOS:**
```typescript
await shell.execute('dir', 'List files');  
// ❌ DENY: "dir is a Windows command. Use 'ls' on Unix systems."
```

### Agent Self-Correction

Agents receive clear feedback and learn to use correct commands:

```
Turn 1: "Run ls -la" → DENY ("Use 'dir' on Windows")
Turn 2: "Run dir" → ALLOW → Success!
```

## Platform-Specific Examples

### File Listing

| Windows | Unix |
|---------|------|
| `dir` | `ls` |
| `dir /s` | `ls -R` |
| `dir /a` | `ls -a` |

### File Operations

| Windows | Unix |
|---------|------|
| `copy` | `cp` |
| `move` | `mv` |
| `del` | `rm` |
| `type` | `cat` |

### Path Separators

| Windows | Unix |
|---------|------|
| `C:\Users\name` | `/home/name` |
| `.\file.txt` | `./file.txt` |
| Backslash (`\`) | Forward slash (`/`) |

## Manual OS Override

In rare cases, you can override OS detection:

```typescript
const shell = new SecureShell({
    osInfo: 'Linux Ubuntu 22.04'
});
```

Useful for:
- Testing cross-platform behavior
- Remote execution scenarios
- Container environments

## Gatekeeper Integration

The gatekeeper receives OS context

 in every evaluation:

```
Command: rm -rf /tmp/cache
OS: Windows 10
Risk: RED

Decision: DENY
Reason: "rm is not available on Windows. Use 'del' or 'Remove-Item' instead."
```

## Best Practices

1. **Let it auto-detect** - Don't override unless necessary
2. **Trust the blocking** - Platform mismatches are real errors
3. **Use agent feedback** - Let agents learn from denials
4. **Test on target OS** - Deploy agents on their actual environment

## Next Steps

- [Zero-Trust Gatekeeper](gatekeeper.md) - How platform-aware evaluation works
- [Risk Classification](risk-classification.md) - Command categorization
