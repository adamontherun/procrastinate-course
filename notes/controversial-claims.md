# Adversarial cross-check adjudication

Harness: `cursor-agent` / `gpt-5.3-codex-xhigh` (2026-07-06).

## P1-19 — worker `name=` (DISPUTED)

**Claim:** `name=` labels log lines only; DB row has id/heartbeat, not name.

**Verdict:** Partially wrong. Source confirms `worker_name` is stored on the worker, passed into `JobContext`, and used for child loggers — not logs-only.

**Fix:** ch04.html updated to mention `JobContext.worker_name`; DB registration caveat kept.

## P2-12 — lock-release polling timings (UNVERIFIABLE)

**Claim:** ~5.6s vs ~1.2s benchmark with default vs 0.2s polling.

**Verdict:** Mechanism confirmed from source; timings are from `examples/ch07_locks.py` captured output in the book, not fabricated.

**Fix:** None.

## P2-14 — priority starvation "months" quote (UNVERIFIABLE)

**Claim:** Docs warn low-priority jobs could take months under constant load.

**Verdict:** Confirmed — exact wording on priorities guide page, already cited inline in ch07.

**Fix:** None.

## P2-18 — middleware new in 3.9.0 (UNVERIFIABLE)

**Claim:** Task/worker middleware absent in older 3.x.

**Verdict:** Confirmed — `middleware.py` absent in 3.7.0/3.8.0 tags, present in 3.9.0.

**Fix:** None.

## P4-07 — migration filename pattern (DISPUTED)

**Claim:** All migrations named `{version}_{serial}_{pre|post}_description.sql`.

**Verdict:** Pattern applies to 3.x migrations; legacy files (e.g. `00.17.00_01_...`) omit pre/post.

**Fix:** ch12.html softened to distinguish 3.x pre/post files from legacy names.

## P4-09 — logging logger name and action extra (DISPUTED)

**Claim:** All logging goes to `procrastinate` logger; every record has `action` extra.

**Verdict:** Workers use `procrastinate.worker` child loggers; `action` is common on worker lifecycle records but not universal on every log line.

**Fix:** ch12.html softened wording.
