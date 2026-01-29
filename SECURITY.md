# Security Policy

## Reporting Security Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in SecureShell, please report it privately to:

**Email:** keshav.r.1925@gmail.com

Include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

We will acknowledge your email within 48 hours and send a more detailed response within 7 days indicating the next steps in handling your report.

## Security Update Process

1. The security issue is received and assigned to a primary handler
2. The problem is confirmed and affected versions are determined
3. Code is audited to find any similar problems
4. Fixes are prepared for all supported versions
5. New versions are released and announced

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Security Best Practices

When using SecureShell:

1. **API Keys**: Never commit API keys to version control. Use environment variables or secure secret management.

2. **Audit Logs**: Enable audit logging in production to track all command executions:
   ```python
   shell = SecureShell(audit_log="secureshell_audit.jsonl")
   ```

3. **Gatekeeper LLM**: Use a reliable LLM provider for the gatekeeper. Unreliable models may approve dangerous commands.

4. **Template Selection**: Choose appropriate security templates:
   - `strict`: Production environments
   - `development`: Development only
   - `custom`: Carefully review allowed/blocked commands

5. **Sandbox Paths**: Configure `allowed_dirs` to restrict file system access:
   ```python
   shell = SecureShell(
       sandbox_config={
           "allowed_dirs": ["/home/user/project"],
           "blocked_commands": ["rm", "dd", "mkfs"]
       }
   )
   ```

6. **Regular Updates**: Keep SecureShell updated to receive security patches.

## Known Security Considerations

- **LLM Dependency**: SecureShell's security relies on the gatekeeper LLM's judgment. While robust, it's not infallible.
- **Prompt Injection**: Sophisticated adversarial inputs might attempt to manipulate the gatekeeper. Defense mechanisms are in place but evolving.
- **Performance**: Gatekeeper evaluation adds latency. Balance security with performance needs.

## Acknowledgments

We thank security researchers and the community for responsibly disclosing vulnerabilities and helping improve SecureShell's security.
