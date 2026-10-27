# Security Audit - Social Network API

5 potential exposures

| **Exposure case** | **Consequence** | **Control** | **Test** |
|---|---|---|---|
| **Passwords stored as plaintext or fast hashes** | Password database compromise exposes credentials | Use Argon2id or appropriate password hash with salt and calibrated cost; never log passwords | Inspect storage and logging; verify password hashes and rehash behavior |
| **JWT validation permits unsafe algorithms or skips claim checks** | Forged or cross-service tokens may be accepted | Pin allowed signing algorithms; check signature, `exp`, intended issuer and audience | Negative tests using invalid signature, expired token and incorrect issuer/audience |
| **Tokens or API credentials leaked in URLs, logs, source code or browser storage** | Account takeover / credential abuse | Use HTTPS and Authorization header; avoid logging secrets; store secrets in secret management; choose secure client storage | Review logs, git history and telemetry for token leakage |
| **Overly broad scopes or admin access based only on authentication** | Broken Function Level Authorization | Enforce scope/role at each operation and least privilege | User with no `posts:read` gets `403`; admin-only actions separately protected |
| **Serialization leaks internal or sensitive post/user fields** | Information disclosure / property-level authorization issue | Explicit response schemas/DTO allowlists, avoid raw ORM dumps | Assert sensitive fields do not appear in responses |