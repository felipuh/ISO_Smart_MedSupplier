# OWASP ASVS L2 Checklist

- Authentication delegated to existing Iso Smart/AdminApps controls.
- Object-level authorization enforced for MedSupplier resources.
- Tenant and account scoping enforced server-side.
- Sensitive fields removed from Customer serializers.
- Sensitive workflow actions require reason capture.
- Audit events include actor, object, time, IP/user-agent, correlation ID, and hash.
- No secrets are introduced in code.
