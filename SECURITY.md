# Security Policy

## Supported Versions

Security fixes are applied on the `main` branch. Pin dependencies via lockfiles and update regularly.

## Reporting a Vulnerability

- Create a private security advisory or contact maintainers.
- Do not open public issues with exploit details.

## Secrets Management

- Use `.env.template` and never commit real secrets.
- Rotate credentials regularly; avoid default passwords.
- Prefer secret managers (Vault/KMS) in production.

## Dependency Security

- Enable dependency review and automated updates.
- Run `npm audit`/`pip-audit` in CI.

## Data Protection

- Mask PII in logs; avoid storing raw sensitive data.
- Hash with SHA-256 or stronger; avoid md5.

## LLM Safety (if applicable)

- Sanitize inputs; enforce size limits and content filters.
- Prevent prompt injection via allowlists and strict tool routing.








