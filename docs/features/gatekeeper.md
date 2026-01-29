# Zero-Trust Gatekeeper

The Zero-Trust Gatekeeper is SecureShell's core security feature. It uses an LLM to evaluate commands before execution, treating every command as untrusted until validated.

## How It Works

For YELLOW or RED risk commands, the gatekeeper:
1. Receives command + reasoning from agent
2. Analyzes command in context of risk, OS, and security policy
3. Makes decision: ALLOW, DENY, or CHALLENGE
4. Returns reasoning explaining the decision

## Decision Types

**ALLOW** - Command is safe to execute

**DENY** - Command is too dangerous or inappropriate  

**CHALLENGE** - Needs clarification (treated as DENY, agent can provide better reasoning and retry)

## Platform-Aware Evaluation

The gatekeeper understands platform differences:

```typescript
// On Windows
await shell.execute('ls -la', 'List files');
// Decision: DENY
// Reason: "ls is Unix-only. Use 'dir' on Windows."
```

This helps agents learn and self-correct automatically.

## Configuration

**Enable/Disable:**
```typescript
const shell = new SecureShell({
    config: { gatekeeperEnabled: true } // default
});
```

**Risk Threshold** - Control which commands trigger gatekeeper:
```typescript
const shell = new SecureShell({
    config: { riskThreshold: 'YELLOW' } // YELLOW and RED (default)
});
```

Options: `'GREEN'` (all), `'YELLOW'` (default), `'RED'` (only high-risk)

**LLM Provider:**
```typescript
// Fast: OpenAI
new SecureShell({ provider: new OpenAIProvider({ apiKey: '...', model: 'gpt-4o-mini' }) });

// Strong reasoning: Anthropic
new SecureShell({ provider: new AnthropicProvider({ model: 'claude-3-5-sonnet-20241022' }) });

// Private: Local model
new SecureShell({ provider: new OllamaProvider({ model: 'llama3' }) });
```

## Fail-Safe Behavior

```typescript
const shell = new SecureShell({
    config: { failClosed: true } // default: deny on error
});
```

- `failClosed: true` - Deny if gatekeeper fails (safe default)
- `failClosed: false` - Allow if gatekeeper fails (risky)

## Agent Learning

Agents learn from gatekeeper feedback:

```
Turn 1: Agent tries "ls -la" → DENY ("Use 'dir' on Windows")
Turn 2: Agent tries "dir" → ALLOW → Success!
```

## Example Evaluations

**Safe development:**
```
Command: git commit -m "Fix bug"
Decision: ALLOW
Reason: "Standard version control, no destructive effects"
```

**Dangerous with poor reasoning:**
```
Command: rm -rf /var
Decision: DENY
Reason: "Would break system. Never acceptable."
```

**Scoped deletion:**
```
Command: rm -rf build
Decision: ALLOW
Reason: "Removing ./build is standard for cleaning artifacts"
```

## Security Templates

Templates configure gatekeeper strictness:
- **Paranoid** - Denies almost everything, extreme caution
- **Production** - Balanced, allows common operations
- **Development** - Permissive for dev workflows  
- **CI/CD** - Optimized for automation

See [Security Templates](security-templates.md).

## Best Practices

1. **Good reasoning** - Help gatekeeper understand intent
2. **Choose appropriate template** - Match your use case
3. **Monitor logs** - Review decisions in audit trail
4. **Let agents learn** - Don't bypass, let them self-correct

## Next Steps

- [Risk Classification](risk-classification.md) - How commands are categorized
- [Security Templates](security-templates.md) - Pre-configured policies
- [Audit Logging](audit-logging.md) - Track decisions


## How It Works

When a YELLOW or RED risk command is submitted, the gatekeeper:

1. **Receives command + reasoning** from the agent
2. **Analyzes** the command in context of:
   - Risk classification
   - Operating system  
   - Agent's stated reasoning
   - Security policy
3. **Makes decision**: ALLOW, DENY, or CHALLENGE
4. **Returns reasoning** explaining the decision

## Decision Types

### ALLOW

Command is safe to execute.

**Example:**
```
Command: mkdir ./build
Reasoning: Creating build output directory

Gatekeeper Decision: ALLOW
Gatekeeper Reasoning: "Creating a build directory is a standard development practice and poses no risk"
```

### DENY

Command is too dangerous or inappropriate.

**Example:**
```
Command: rm -rf /
Reasoning: Clean up files

Gatekeeper Decision: DENY
Gatekeeper Reasoning: "This command would delete the entire filesystem. Never acceptable regardless of reasoning."
```

### CHALLENGE

Command needs clarification or confirmation.

**Example:**
```
Command: rm -rf node_modules
Reasoning: Clean up

Gatekeeper Decision: CHALLENGE
Gatekeeper Reasoning: "Please confirm: Are you sure you want to delete node_modules? This will require reinstalling all dependencies."
```

**Note:** CHALLENGE is treated as DENY in current implementation. Agent can provide better reasoning and retry.

## Gatekeeper Prompt

The gatekeeper receives a structured prompt:

```
You are a security gatekeeper evaluating shell commands.

Command: {command}
Risk Tier: {tier}
Agent Reasoning: {reasoning}
OS: {os_info}

Evaluate this command and respond with:
- ALLOW: Safe to execute
- DENY: Too dangerous
- CHALLENGE: Needs clarification

Provide clear reasoning for your decision.
```

## Platform-Aware Evaluation

The gatekeeper understands platform differences:

**On Windows:**
```typescript
await shell.execute('ls -la', 'List files');
// Decision: DENY
// Reasoning: "ls is a Unix command. On Windows, use 'dir' instead."
```

**On Linux:**
```typescript
await shell.execute('dir', 'List files');
// Decision: DENY  
// Reasoning: "dir is a Windows command. On Linux, use 'ls' instead."
```

This helps agents learn and self-correct.

## Configuration

### Enable/Disable

```typescript
// TypeScript
const shell = new SecureShell({
    config: {
        gatekeeperEnabled: true // default
    }
});
```

```python
# Python
shell = SecureShell(
    config=SecureShellConfig(gatekeeper_enabled=True)
)
```

### Risk Threshold

Control which commands trigger gatekeeper:

```typescript
const shell = new SecureShell({
    config: {
        riskThreshold: 'YELLOW' // Evaluate YELLOW and RED
    }
});
```

Options:
- `'GREEN'` - Evaluate everything
- `'YELLOW'` - Evaluate YELLOW and RED (default)
- `'RED'` - Only evaluate RED

### LLM Provider

Choose which LLM powers the gatekeeper:

```typescript
// OpenAI (fast, reliable)
new SecureShell({
    provider: new OpenAIProvider({ 
        apiKey: '...', 
        model: 'gpt-4o-mini' 
    })
});

// Anthropic (strong reasoning)
new SecureShell({
    provider: new AnthropicProvider({ 
        apiKey: '...', 
        model: 'claude-3-5-sonnet-20241022' 
    })
});

// Local (private, offline)
new SecureShell({
    provider: new OllamaProvider({ 
        model: 'llama3',
        endpoint: 'http://localhost:11434'
    })
});
```

## Fail-Safe Behavior

If the gatekeeper fails (API error, timeout, etc.):

```typescript
const shell = new SecureShell({
    config: {
        failClosed: true // default: deny on error
    }
});
```

- **`failClosed: true`** (default) - Deny command if gatekeeper fails
- **`failClosed: false`** - Allow command if gatekeeper fails (risky!)

## Agent Learning

The gatekeeper helps agents learn by providing:

1. **Clear error messages** - "ls is not available on Windows"
2. **Alternatives** - "Use 'dir' instead"
3. **Context** - "This command would delete your entire filesystem"

Agents can use this feedback to self-correct:

```
Iteration 1:
Agent: "Run ls -la"
Gatekeeper: DENY - "Use 'dir' on Windows"

Iteration 2:
Agent: "Run dir"
Gatekeeper: ALLOW
Success!
```

## Example Evaluations

### Safe Development Command
```
Command: git commit -m "Fix bug"
Reasoning: Committing code changes
Risk: YELLOW

Decision: ALLOW
Reasoning: "git commit is a standard version control operation with no destructive effects"
```

### Dangerous Command with Poor Reasoning
```
Command: rm -rf /var
Reasoning: Cleaning up
Risk: RED

Decision: DENY
Reasoning: "Deleting /var would break system functionality. This is never acceptable."
```

### Ambiguous Command
```
Command: rm -rf build
Reasoning: Clean build artifacts
Risk: RED

Decision: ALLOW
Reasoning: "Removing ./build directory is a common development practice for cleaning build artifacts. The path is relative and scoped."
```

### Platform Mismatch
```
Command: powershell -Command "Remove-Item file.txt"
Reasoning: Delete file
Risk: YELLOW
OS: Linux

Decision: DENY
Reasoning: "PowerShell is not typically available on Linux. Use 'rm file.txt' instead."
```

## Security Templates & Gatekeeper

Templates configure gatekeeper strictness:

**Paranoid:**
- Denies almost everything
- Requires extremely strong reasoning
- Even GREEN commands evaluated

**Production:**
- Balanced evaluation
- Allows common operations
- Strict on destructive commands

**Development:**
- Permissive for dev workflows
- Allows most YELLOW commands
- Still blocks obvious dangers

**CI/CD:**
- Optimized for automation
- Allows build/deploy commands
- Fast gatekeeper responses

See [Security Templates](security-templates.md).

## Troubleshooting

### Gatekeeper always denies

**Cause:** Too strict template or threshold.

**Solution:**
```typescript
const shell = new SecureShell({
    template: 'development', // More permissive
    config: { riskThreshold: 'RED' } // Only evaluate RED
});
```

### Gatekeeper disabled warning

**Cause:** No valid LLM provider configured.

**Solution:** Set API key and provider:
```typescript
const shell = new SecureShell({
    provider: new OpenAIProvider({ apiKey: process.env.OPENAI_API_KEY })
});
```

### Slow gatekeeper responses

**Cause:** LLM API latency.

**Solutions:**
- Use faster model (gpt-4o-mini vs gpt-4)
- Use local model (Ollama)
- Increase timeout
- Lower risk threshold

## Best Practices

1. **Good reasoning** - Help gatekeeper understand intent
2. **Specific commands** - Avoid vague or overly complex commands
3. **Template selection** - Choose appropriate template for use case
4. **Monitor logs** - Review gatekeeper decisions in audit logs
5. **Iterate** - Let agents learn from denials

## Next Steps

- [Risk Classification](risk-classification.md) - How commands are categorized
- [Security Templates](security-templates.md) - Pre-configured policies
- [Audit Logging](audit-logging.md) - Track gatekeeper decisions
- [Platform Awareness](platform-awareness.md) - OS-specific evaluation
