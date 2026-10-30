# DNS And SSL Go-Live Runbook

Date: 2026-06-30

Scope: DNS and TLS setup for the DigitalOcean VPS target.

## Status

Current status: READY-NOT-EXECUTED.

No final VPS IP or domain has been provided.

## DNS Plan

Recommended records:

| Name | Type | Value | TTL |
| --- | --- | --- | --- |
| `medsupplier.<domain>` | A | `<digitalocean_vps_ipv4>` | 300 |
| `www.medsupplier.<domain>` | CNAME | `medsupplier.<domain>` | 300 |

If IPv6 is configured:

| Name | Type | Value | TTL |
| --- | --- | --- | --- |
| `medsupplier.<domain>` | AAAA | `<digitalocean_vps_ipv6>` | 300 |

## DNS Verification

```bash
dig +short medsupplier.<domain> A
dig +short www.medsupplier.<domain> CNAME
nslookup medsupplier.<domain>
curl -I http://medsupplier.<domain>/health
```

Expected:
- A record resolves to VPS IP.
- HTTP reaches Nginx.
- `/health` returns success before TLS enforcement.

## Nginx Precheck

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I http://medsupplier.<domain>/
```

## Certbot Procedure

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d medsupplier.<domain> -d www.medsupplier.<domain>
```

Select redirect HTTP to HTTPS when prompted.

## TLS Verification

```bash
curl -I https://medsupplier.<domain>/health
curl -I https://medsupplier.<domain>/ready
openssl s_client -connect medsupplier.<domain>:443 -servername medsupplier.<domain> </dev/null 2>/dev/null | openssl x509 -noout -issuer -subject -dates
sudo certbot renew --dry-run
```

## Required Security Headers

Verify:

```bash
curl -I https://medsupplier.<domain>/
```

Expected minimum:
- `X-Frame-Options`
- `X-Content-Type-Options`
- `Referrer-Policy`
- `Cross-Origin-Opener-Policy`
- HTTPS redirect from HTTP

HSTS preload:
- Do not enable preload until domain ownership, subdomain coverage, and rollback policy are approved.

## Go-Live Checklist

- DNS A record resolves.
- Nginx config test passes.
- Certificate issued.
- HTTP redirects to HTTPS.
- `/health` works over HTTPS.
- `/ready` works over HTTPS.
- Certbot renewal dry-run passes.
- Security headers present.
- Human approval recorded.
