# Risk Classification

SecureShell uses a three-tier risk classification system to categorize commands before they reach the gatekeeper.

## Risk Tiers

### 🟢 GREEN - Low Risk

Commands that are safe and read-only.

**Examples:**
- `ls`, `dir` - List files
- `pwd`, `cd` - Navigate directories
- `cat`, `type` - Read files
- `echo` - Print text
- `whoami` - Show current user
- `date`, `time` - Display time
- `env` - Show environment variables (read-only)

**Behavior:**
- **No gatekeeper evaluation** - Executes immediately
- Still subject to sandbox path restrictions
- Logged in audit trail

### 🟡 YELLOW - Medium Risk

Commands that modify state but are

 typically safe with oversight.

**Examples:**
- `mkdir` - Create directory
- `touch` - Create empty file
- `cp`, `copy` - Copy files
- `mv`, `move`, `ren` - Move/rename
- `git add`, `git commit` - Version control
- `npm install` - Install dependencies
- `python script.py` - Run scripts

**Behavior:**
- **Gatekeeper evaluates** before execution
- Requires reasoning from agent
- May be allowed, denied, or challenged
- Logged with gatekeeper decision

### 🔴 RED - High Risk

Commands that can cause irreversible damage or security issues.

**Examples:**
- `rm -rf /`, `del /f /s /q` - Recursive delete
- `dd` - Disk operations
- `mkfs`, `format` - Format drives
- `chmod 777` - Dangerous permissions
- `curl ... | bash` - Execute remote code
- `:(){ :|:& };:` - Fork bombs
- `sudo` commands - Privilege escalation

**Behavior:**
- **Gatekeeper evaluates** with high scrutiny
- Almost always denied unless strong reasoning
- Requires explicit approval in some templates
- Heavily logged

## Classification Logic

The risk classifier uses regex patterns to match commands:

```typescript
// TypeScript example
const classifier = new RiskClassifier();
const tier = classifier.classify('rm -rf /');
// Returns: RiskTier.RED
```

```python
# Python example
classifier = RiskClassifier()
tier = classifier.classify('rm -rf /')
# Returns: RiskTier.RED
```

## Custom Risk Patterns

You can customize risk classification (advanced):

```typescript
// TypeScript
const shell = new SecureShell({
    config: {
        // Treat all npm commands as GREEN
        customGreenPatterns: ['^npm (list|ls|view)'],
        // Treat specific commands as RED
        customRedPatterns: ['^dangerous-tool']
    }
});
```

## Risk Threshold

Set minimum risk level that triggers gatekeeper:

```typescript
const shell = new SecureShell({
    config: {
        riskThreshold: 'YELLOW' // Only evaluate YELLOW and RED
    }
});
```

Options:
- `'GREEN'` - Evaluate everything (very strict)
- `'YELLOW'` - Evaluate YELLOW and RED (default)
- `'RED'` - Only evaluate RED commands (permissive)

## Pattern Examples

### GREEN Patterns
```regex
^(ls|dir)(\s|$)         # List files
^pwd$                   # Print working directory
^echo\s                 # Echo command
^cat\s+[^\|>]          # Cat without pipes
```

### YELLOW Patterns
```regex
^(mkdir|md)(\s|$)       # Make directory
^git\s+(add|commit)     # Git operations
^npm\s+install          # Package install
^(cp|copy)\s            # Copy files
```

### RED Patterns
```regex
^rm\s+-rf\s+/           # Recursive delete root
^dd\s+if=               # Disk operations
^chmod\s+777            # Dangerous permissions
\|\s*bash$              # Pipe to bash
```

## Bypassing Classification

Some commands may be misclassified. Use gatekeeper reasoning:

```typescript
// Command classified as RED but is actually safe
await shell.execute(
    'rm -rf ./test-output',
    'Cleaning up test directory - only removing ./test-output folder'
);
// Gatekeeper will evaluate context and may allow
```

## Template Overrides

Security templates can override risk behavior:

**Paranoid Template:**
- GREEN commands still pass through gatekeeper
- YELLOW and RED almost always denied

**Development Template:**
- GREEN commands execute immediately
- YELLOW commands usually allowed with basic reasoning
- RED commands require strong reasoning

See [Security Templates](security-templates.md) for details.

## Audit Trail

All commands are logged with their risk tier:

```json
{
  "timestamp": "2026-01-30T01:00:00.000Z",
  "command": "ls -la",
  "risk_tier": "GREEN",
  "gatekeeper_decision": null,
  "success": true
}
```

```json
{
  "timestamp": "2026-01-30T01:00:05.000Z",
  "command": "rm -rf /tmp/cache",
  "risk_tier": "RED",
  "gatekeeper_decision": "ALLOW",
  "gatekeeper_reasoning": "Removing temporary cache folder is safe",
  "success": true
}
```

## Best Practices

1. **Trust the classification** - Don't bypass it without good reason
2. **Provide context** - Good reasoning helps gatekeeper make better decisions
3. **Review logs** - Check audit logs for misclassifications
4. **Start strict** - Use `paranoid` template initially, relax as needed
5. **Test safely** - Test command patterns in safe environment first

## Next Steps

- [Zero-Trust Gatekeeper](gatekeeper.md) - How commands are evaluated
- [Audit Logging](audit-logging.md) - Understanding the audit trail
- [Security Templates](security-templates.md) - Pre-configured risk policies
