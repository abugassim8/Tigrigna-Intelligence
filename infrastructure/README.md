# Infrastructure

## Purpose of this directory

Everything needed to deploy and operate the platform: container definitions,
orchestration manifests, infrastructure-as-code, and monitoring configuration.

## Why this directory exists

Low operating cost is a stated project priority (**A-008**, **P-6**), and
infrastructure is where that priority is either honoured or quietly abandoned.
Keeping deployment definitions in the repository also serves reproducibility
(**P-5**): the running system should be derivable from what is committed here.

## Structure

| Directory | Contents |
| --- | --- |
| `docker/` | Dockerfiles, compose files, base images |
| `kubernetes/` | Manifests and Helm charts, **if** Kubernetes is justified |
| `terraform/` | Infrastructure-as-code for cloud resources |
| `monitoring/` | Metrics, logging, alerting, and dashboard configuration |

## The governing constraint

**Optimise for cost at low volume sustained over years — not for scale we do not
have.**

Most infrastructure guidance optimises for the opposite. Following it here would
mean paying continuously for capacity nobody uses. Kubernetes in particular is
scaffolded above but **not assumed**: whether it is justified at this project's
size is an open research question, and something simpler may well be the right
answer. See **N-8**, **P-6**, **P-7**.

## Rules

1. **No secrets, ever.** Not in manifests, not in Terraform, not in compose
   files, not in git history. Use environment variables and a secrets manager;
   document required variables in the relevant README.
2. **Reproducible.** Infrastructure is defined in code, not clicked into
   existence in a console.
3. **Costed.** Every component records what it costs to run per month.
4. **Boring.** Well-supported, widely-used tooling (**P-7**). Interesting
   infrastructure fails in interesting ways at inconvenient times.

## Gated on

`../docs/research/reports/10_infrastructure/` and `05_architecture/`.

## What future contributors should add

Deployment definitions, once there is something to deploy. Record actual
measured monthly cost per component — estimates get stale, and the difference
between estimated and actual cost is one of the more useful things to know.

## Status

**Empty.** Nothing to deploy.
