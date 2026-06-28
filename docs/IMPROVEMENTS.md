# Aladhan — Improvement Backlog & Future Roadmap

A living, prioritized list of what to improve, grounded in the current code and
the operational issues we hit running it on the home k3s cluster. Priorities:
**P0** = correctness/reliability/security worth doing soon, **P1** = high-value,
**P2** = nice-to-have. Effort is a rough T-shirt size.

---

## 1. Reliability & Operations (the home cluster)

These caused real, user-visible outages during operation — they're the highest leverage.

| # | Item | Pri | Effort | Notes |
|-|-|-|-|-|
| 1.1 | **Pick ONE LoadBalancer controller** | P0 | M | k3s servicelb (klipper) **and** MetalLB both run and fight: Traefik flipped off its MetalLB IP (.43) onto the node IP, silently breaking every `.home` name. Currently worked around with `lanIngressIP = node IP`. Proper fix: `k3s --disable servicelb` so MetalLB owns the pool (needs a k3s restart). See `k8s-project/docs/dns-setup.md`. |
| 1.2 | **Single point of failure** | P1 | M | One Pi = DNS, ingress and app all die together. A second small resolver (or Pi-hole HA) keeps the LAN resolving if the Pi reboots. At minimum, document the blast radius. |
| 1.3 | **Reproducible deploys (pin digests)** | P1 | S | `:latest` + `imagePullPolicy: Always` does **not** reliably re-pull on k3s/containerd (cached digest). The in-app "Update" now pins by digest; apply the same idea in CI/CD so a deploy is reproducible and rollback is trivial. |
| 1.4 | **Adopt Keel or finish GitOps for all apps** | P1 | M | Only `adhan` is under Argo CD; Pi-hole is still helm-managed by hand and diverged on the node. Bring Pi-hole under Argo (reconcile the v6/unbound/NodePort config into git first). |
| 1.5 | **Backups** | P1 | S | The adhan DB, Pi-hole config and Freebox token live on a node `hostPath` (`/home/pi/data`). One SD-card failure loses everything. Add a periodic backup (cron → off-Pi). |
| 1.6 | **`.home` is fragile on Apple devices** | P2 | M | macOS/iOS `getaddrinfo` special-cases the made-up `.home` TLD (apps fail, `dig` works). Per-device `/etc/resolver/home` is the stopgap. A real (even free) domain with a record → LAN IP removes the quirk for every device/DoH. |
| 1.7 | **Observability** | P2 | M | No metrics/alerting. A light Prometheus + a "is the next adhan scheduled?" alert would catch silent scheduler failures. Logs already structured. |

## 2. Security

| # | Item | Pri | Effort | Notes |
|-|-|-|-|-|
| 2.1 | **No app authentication** | P0 | M | Anyone on the LAN can change settings, upload audio, **force a redeploy** (`/update/force`) and trigger playback. Acceptable for a trusted home LAN, but a simple shared PIN / token gate on mutating + update routes is cheap insurance. |
| 2.2 | **Least-privilege RBAC** | — | — | Already good: the force-update ServiceAccount can only `get/patch` its own Deployment. Keep new privileges this tight. |
| 2.3 | **Secrets hygiene** | P1 | S | Pi-hole password via `existingSecret` (good). Audit that no token/password is committed (the `.fbx_token.json` is git-ignored — keep it so). Consider sealed-secrets/SOPS if the repo ever goes public. |
| 2.4 | **Input validation at boundaries** | P2 | S | Audio upload and city/settings endpoints should validate size/type/range explicitly (Pydantic helps; confirm upload limits). |

## 3. Frontend

| # | Item | Pri | Effort | Notes |
|-|-|-|-|-|
| 3.1 | **Zero frontend tests** | P0 | M | No unit/component tests at all. Add Vitest + React Testing Library for the high-risk bits first: prayer-time formatting, device control flow, the update/changelog hooks, city search. |
| 3.2 | **1 MB JS bundle** | P1 | S | The main chunk is ~1 MB; `jspdf` (386 KB) + `html2canvas` (201 KB) are bundled eagerly but only used for PDF export. Lazy-load them with `import()` behind the "Export PDF" action; add `manualChunks`. |
| 3.3 | **46 TODO/FIXME** | P1 | M | Triage them — convert real ones to issues, delete stale ones. |
| 3.4 | **Accessibility & reduced-motion** | P2 | S | Verify keyboard focus on the device cards/dialogs and honour `prefers-reduced-motion` for the animations. |
| 3.5 | **A few `defaultValue` i18n keys are missing** | P2 | S | `deviceInfo.*` relies on inline `defaultValue` and isn't translated. Move them into the locale files for full i18n. |

## 4. Backend

| # | Item | Pri | Effort | Notes |
|-|-|-|-|-|
| 4.1 | **`device_service.py` is 633 lines** | P1 | M | It mixes discovery, network introspection, scheduling and per-backend control. Split per concern (discovery / network / playback / scheduler) for testability. |
| 4.2 | **Expand test coverage** | P1 | M | 8 backend test files exist (good base). Add tests around the prayer engine edge cases (DST, high latitude), the scheduler singleton, and the new `/update/*` + `/changelog` routes. |
| 4.3 | **Consistent error handling** | P2 | S | Several `try/except: pass` best-effort blocks (device info, state). Fine for telemetry, but ensure none hides a real failure of a user action (see the team's "never swallow errors that mean the action failed" rule). |
| 4.4 | **Version source of truth** | — | — | Unified via `src/utils/version.py` (good). Keep `pyproject` the single source. |

## 5. Developer Experience / CI-CD

| # | Item | Pri | Effort | Notes |
|-|-|-|-|-|
| 5.1 | **CI gate: lint + typecheck + tests** | P0 | S | `publish.yml` only builds/pushes the image. Add a job that runs `ruff`/`pytest` (backend) and `tsc`/`eslint`/`vitest` (frontend) and **fails the build** on error — would have caught the `uv.lock` drift before it broke the image build. |
| 5.2 | **Automate version bump + lockfile** | P1 | S | Bumping `pyproject` without `uv lock` broke CI once. A `make release` / script that bumps front+back versions, runs `uv lock`, regenerates the changelog and tags would remove the foot-guns. |
| 5.3 | **Changelog: curated, not raw git** | — | — | Switched from raw `git log` to a curated `changelog.json` (good). Keep curating per release; `gen_changelog.py` remains as a seed helper. |
| 5.4 | **Git tags per release** | P2 | S | There are no tags. Tagging `vX.Y.Z` makes rollbacks, changelog ranges and "what's deployed" unambiguous. |

---

## Suggested order (next few iterations)

1. **CI gate** (5.1) + **frontend tests bootstrap** (3.1) — stop regressions.
2. **One LB controller** (1.1) + **backups** (1.5) — kill the recurring infra fragility.
3. **App auth gate** (2.1) — before exposing anything beyond the trusted LAN.
4. **Bundle code-splitting** (3.2) + **release automation** (5.2) — polish & velocity.

> Keep this file updated as items land — it doubles as the engineering changelog
> of "why" decisions (the in-app changelog covers "what").
