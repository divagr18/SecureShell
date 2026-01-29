# Security Templates

Security templates are pre-configured security profiles for common use cases. Instead of manually configuring allowlists, blocklists, and risk thresholds, choose a template that matches your needs.

## Available Templates

### Paranoid

Maximum security - blocks almost everything.

**Use when:** Production systems, untrusted agents, high-security environments

**Behavior:**
- Evaluates even GREEN commands
- Denies most YELLOW/RED commands
- Requires extremely strong reasoning
- Minimal allowlist

```typescript
const shell = new SecureShell({ template: 'paranoid' });
```

### Production

Balanced security for production environments.

**Use when:** Production agents, automated systems, customer-facing tools

**Behavior:**
- Allows safe read operations
- Evaluates modifications carefully
- Blocks dangerous operations
- Moderate allowlist

```typescript
const shell = new SecureShell({ template: 'production' });
```

### Development

Permissive for development workflows.

**Use when:** Local development, testing, prototyping

**Behavior:**
- GREEN commands execute immediately
- YELLOW commands usually allowed
- RED commands require good reasoning
- Generous allowlist

```typescript
const shell = new SecureShell({ template: 'development' });
```

### CI/CD

Optimized for automated pipelines.

**Use when:** Build servers, deployment automation, CI/CD

**Behavior:**
- Fast gatekeeper responses
- Allows build/deploy commands
- Blocks user-interactive commands
- Build-focused allowlist

```typescript
const shell = new SecureShell({ template: 'ci_cd' });
```

## Template Comparison

| Feature | Paranoid | Production | Development | CI/CD |
|---------|----------|------------|-------------|-------|
| GREEN auto-allow | ❌ | ✅ | ✅ | ✅ |
| YELLOW permissive | ❌ | ⚠️ | ✅ | ✅ |
| RED blocking | ✅ | ✅ | ⚠️ | ✅ |
| Speed | Slower | Medium | Fast | Fastest |
| Use case | High security | Production | Development | Automation |

## Customizing Templates

You can override template settings:

```typescript
const shell = new SecureShell({
    template: 'production',
    config: {
        // Override specific settings
        allowlist: ['npm', 'git', 'docker'],
        blocklist: ['rm -rf /', 'dd'],
        riskThreshold: 'RED' // More permissive
    }
});
```

## When to Use Each Template

**Paranoid:**
- Public-facing AI assistants
- Financial/healthcare systems
- Untrusted or experimental agents
- High-stakes environments

**Production:**
- Internal automation tools
- Deployed AI agents
- Customer support bots
- Monitoring systems

**Development:**
- Local development
- Testing new features
- Prototyping agents
- Learning/experimentation

**CI/CD:**
- GitHub Actions
- GitLab CI
- Jenkins pipelines
- Deployment scripts

## Best Practices

1. **Start strict** - Begin with `paranoid`, relax as needed
2. **Match environment** - Use appropriate template for deployment
3. **Override selectively** - Customize only what you need
4. **Test thoroughly** - Verify behavior before production
5. **Monitor logs** - Review audit logs to refine settings

## Next Steps

- [Risk Classification](risk-classification.md) - Understanding risk tiers
- [Zero-Trust Gatekeeper](gatekeeper.md) - How evaluation works
- [Configuration](../configuration.md) - Advanced customization
