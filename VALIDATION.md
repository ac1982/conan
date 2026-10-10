# Hub validation

Prepared on 2026-10-10. This records local verification, not remote CI success.

## Hub checks

- Standard-library unit suite: 13 tests passed.
- All manifests and SHA-256 patch/license hashes validated.
- Invalid paths, symlinked inputs/destinations, unpinned commits, non-HTTPS upstreams,
  tampered files, unsupported patch modes and existing targets are rejected.
- Git invocations use argument lists without a shell, disable hooks and inherited
  configuration, and block protocols other than HTTPS (plus explicitly requested
  local cloning). Tests do not fetch or execute upstream project code.

Independent hub review found a failure-path push-guard gap: a failed fetch could
leave a partial checkout without its disabled push URL. The guard now precedes
fetch and is installed during offline clone creation; regression tests cover both.

## Exact-baseline application

Each project was materialized into a new local clone from available committed Git
objects. The source working trees were not copied. Each checkout's HEAD equaled its
manifest's exact baseline. For all three patches:

1. `git apply --check --index` passed.
2. `git apply --index` passed.
3. Changed paths equaled the manifest's list.
4. Re-emitted staged patch matched the packaged patch byte-for-byte.
5. `git diff --cached --check` passed.

Fresh tests on those materialized patched trees:

- Cyclopts configuration suite: 135 passed; import location verified.
- Mitty full test suite: 234 passed across 9 files.
- LLM embedding suites: 120 passed offline; import location verified.

Existing development environments were reused only for those explicit local tests.
The materialization script itself never installs dependencies or runs cloned code.
Project-wide checks already performed during implementation/review are summarized
separately in each subproject's `VALIDATION.md`, with their scope and omissions.

## Limits

The public-HTTPS fetch path was not exercised during packaging; the offline local
clone path was exercised for all three exact baselines. Default CI only runs offline
hub tests; upstream tests, remote CI and operating-system/version matrices are not
implied by that green check. No upstream submission is part of this validation.
