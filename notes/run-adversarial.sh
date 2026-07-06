#!/bin/sh
# Adversarial cross-check: one cursor-agent run per part, gpt-5.3-codex-xhigh.
# Read-only research task; raw JSON verdicts land in notes/.
set -u
cd "$(dirname "$0")/.."

run_part() {
  part="$1"; chapters="$2"; ids="$3"
  prompt="You are an independent technical fact-checker. This is a READ-ONLY research-and-report task: do not write, edit, or create any files; only read files and browse the web, then print your report.

Context: a course teaches the Python library procrastinate, version 3.9.0 (PostgreSQL-based task queue). The chapter HTML files to check are: ${chapters}. The file notes/fact-check-manifest.json contains a list of claims; check ONLY the claims whose id starts with '${ids}'.

For each such claim, re-derive your own verdict from scratch using primary sources: the official docs at https://procrastinate.readthedocs.io/en/stable/, the project's GitHub repo (procrastinate-org/procrastinate), PyPI, Docker/AWS official docs where relevant, and the installed package source in .venv/lib/python3.12/site-packages/procrastinate/ (you may read it). Where a claim describes runtime behavior you cannot confirm from documents alone, you may reason from the library source code, but say so.

Print ONLY a JSON array, one object per claim id, shaped exactly like:
[{\"id\": \"P1-01\", \"verdict\": \"CONFIRMED|DISPUTED|UNVERIFIABLE\", \"evidence_url\": \"...\", \"reason\": \"one line\"}]
No prose before or after the JSON."
  out="notes/adversarial-cross-check-part-${part}.json"
  if ! cursor-agent --print --output-format text --trust --model gpt-5.3-codex-xhigh --sandbox enabled "$prompt" > "$out" 2> "notes/adv-part-${part}.err"; then
    echo "part ${part}: sandbox flag failed, retrying without it" >&2
    cursor-agent --print --output-format text --trust --model gpt-5.3-codex-xhigh "$prompt" > "$out" 2> "notes/adv-part-${part}.err"
  fi
  echo "part ${part} done: $(wc -c < "$out") bytes"
}

run_part 1 "book/chapters/ch01.html book/chapters/ch02.html book/chapters/ch03.html book/chapters/ch04.html" "P1-"
run_part 2 "book/chapters/ch05.html book/chapters/ch06.html book/chapters/ch07.html book/chapters/ch08.html" "P2-"
run_part 3 "book/chapters/ch09.html book/chapters/ch10.html" "P3-"
run_part 4 "book/chapters/ch11.html book/chapters/ch12.html book/chapters/ch13.html" "P4-"
echo ALL_PARTS_DONE
