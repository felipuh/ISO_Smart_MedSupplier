# Release Candidate Checklist

Date: 2026-06-30

Release: MedSupplier Controlled Release Candidate

## Technical Checklist

| Item | Status | Evidence |
| --- | --- | --- |
| Backend check | PASS | `manage.py check` |
| Migration drift | PASS | `makemigrations --check --dry-run` |
| Migration plan | PASS | `migrate --plan` no operations |
| PostgreSQL runtime | PASS | `backend.settings` DB engine |
| AdminApps no-fallback smoke | PASS | `check_medsupplier_adminapps --no-fallback` |
| Frontend lint | PASS | `npm run lint` |
| Frontend build | PASS | `npm run build` |
| Deploy check | PASS WITH WARNING | HSTS preload warning only |
| Backup artifact | PASS | PostgreSQL dump generated |
| Backup checksum | PASS | `sha256sum -c` |
| Restore drill | BLOCKED | DBA-created DB required |
| Rollback tabletop | PASS WITH RESTRICTION | `rollback_tabletop_report.txt` |

## Operational Checklist

| Item | Status | Action |
| --- | --- | --- |
| DNS/domain | READY-NOT-EXECUTED | Create records after VPS IP. |
| SSL/TLS | READY-NOT-EXECUTED | Run Certbot after DNS. |
| VPS deployment | READY-NOT-EXECUTED | Follow VPS bridge checklist. |
| Monitoring/alerting | READY-NOT-EXECUTED | Activate minimum monitors. |
| Restore drill | BLOCKED | DBA action required. |
| Rollback rehearsal | READY-NOT-EXECUTED | Execute on VPS. |
| Human approval | PENDING | Complete approval gate. |

## Commercial Checklist

| Item | Status |
| --- | --- |
| Pilot scope | READY |
| Known limitations | READY |
| Support model | READY |
| Success criteria | READY |
| Data classification | READY |
| No regulated claim | PASS |
| No guaranteed compliance claim | PASS |

## Git / Release Checklist

Recommended branch:

```text
release/medsupplier-controlled-rc-2026-06-30
```

Recommended tag:

```text
medsupplier-rc-2026-06-30
```

Recommended commit message:

```text
chore(release): prepare MedSupplier controlled RC go-live readiness
```

Do not push remotely without release owner approval.
