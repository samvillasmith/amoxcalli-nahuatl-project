#!/usr/bin/env python3
"""
simeon_translate_en.py

Translates all French definitions in simeon_parsed.json to English using
the Anthropic API with async concurrent processing and checkpointing.

Input:  simeon_parsed.json      (28,709 entries with definition_fr)
Output: simeon_parsed_en.json   (same structure + definition_en on every entry)
        simeon_translate_checkpoint.json  (deleted on clean completion)

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python simeon_translate_en.py

Resume after interruption:
    python simeon_translate_en.py   # auto-detects checkpoint
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Load .env if present
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

import anthropic

# ── Configuration ─────────────────────────────────────────────────────────────

MODEL              = "claude-sonnet-4-6"
BATCH_SIZE         = 20   # entries per API call
MAX_CONCURRENT     = 25   # high enough that rate limiter is the only bottleneck
REQUESTS_PER_MIN   = 40   # 1 call/1.5s — staggered to prevent burst, ~800 entries/min
LONG_THRESHOLD     = 3000 # chars — process these individually with more tokens

INPUT_FILE  = Path("simeon_parsed.json")
OUTPUT_FILE = Path("simeon_parsed_en.json")
CHECKPOINT  = Path("simeon_translate_checkpoint.json")

SYSTEM_PROMPT = """You are translating entries from Siméon's 1885 French-Nahuatl dictionary
(Dictionnaire de la langue nahuatl ou mexicaine) into English.

RULES:
- Translate all French text into clear, accurate English
- Do NOT translate Nahuatl words — leave them exactly as written
- Adapt French abbreviations to English equivalents:
    Voy. / V.           → See
    p. / P. (prétérit)  → pret.
    fréq.               → freq.
    Rév.                → rev.
    en comp.            → in comp.
    par ext.            → by ext.
    au fig.             → fig.
    litt. / lit.        → lit.
    priv.               → priv.
    s. (substantif)     → n.
    v.                  → v.
    adj.                → adj.
    adv.                → adv.
    R. / RR.            → R. / RR.  (keep root notation as-is)
- Keep author citations unchanged: (Car.), (Olm.), (Par.), (Clav.), (Chim.), (Gau.), (Sah.), etc.
- Keep Nahuatl morphological notation: nino-, nite-, nitla-, mo-, te-, tla-, etc.
- Keep calendar references, preterite forms, and grammatical paradigms as-is
- Preserve structure of multi-sense entries (numbered senses, semicolons, etc.)
- OCR errors in the French are common — translate the intended meaning as best you can

INPUT:  JSON array — [{"id": <int>, "definition_fr": "<French>"}, ...]
OUTPUT: JSON array — [{"id": <int>, "definition_en": "<English>"}, ...]

Return ONLY the JSON array. No explanation, no markdown fences."""


# ── Rate limiter ──────────────────────────────────────────────────────────────

class RateLimiter:
    """Leaky-bucket rate limiter. Lock is held only briefly; sleep happens outside it."""
    def __init__(self, rpm: int) -> None:
        self._interval = 60.0 / rpm
        self._next     = 0.0
        self._lock     = asyncio.Lock()

    async def acquire(self) -> None:
        while True:
            async with self._lock:          # hold lock only to read/update timestamp
                now = time.monotonic()
                if now >= self._next:
                    self._next = now + self._interval
                    return                  # slot is ours, fire immediately
                wait = self._next - now
                self._next += self._interval  # reserve the next slot
            await asyncio.sleep(wait)       # sleep WITHOUT holding the lock


# ── API helpers ───────────────────────────────────────────────────────────────

async def _api_call(
    client: anthropic.AsyncAnthropic,
    payload: list[dict],
    max_tokens: int = 2048,
    rate_limiter: "RateLimiter | None" = None,
) -> list[dict]:
    """Single API call with retry and backoff. Returns parsed JSON list."""
    for attempt in range(5):
        try:
            if rate_limiter:
                await rate_limiter.acquire()
            resp = await client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                }],
            )
            text = resp.content[0].text.strip()

            # Strip markdown fences if the model adds them
            if text.startswith("```"):
                lines = text.splitlines()
                # Drop first line (```json or ```) and last line (```)
                inner = lines[1:] if lines[-1].strip() == "```" else lines[1:]
                if inner and inner[-1].strip() == "```":
                    inner = inner[:-1]
                text = "\n".join(inner)

            return json.loads(text)

        except json.JSONDecodeError as exc:
            if attempt < 4:
                await asyncio.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"JSON parse failed after retries: {exc}") from exc

        except anthropic.RateLimitError:
            wait = 5 * (2 ** min(attempt, 3))   # 5s, 10s, 20s, 40s
            print(f"\n  [rate limit — waiting {wait}s]", flush=True)
            await asyncio.sleep(wait)

        except anthropic.BadRequestError as exc:
            # Credit exhaustion — fail immediately, do not silently store empty strings
            if "credit balance" in str(exc).lower() or "too low" in str(exc).lower():
                print(f"\n\nFATAL: Anthropic API credit balance too low. Add credits at console.anthropic.com and re-run.", file=sys.stderr)
                sys.exit(1)
            raise

        except anthropic.APIStatusError as exc:
            if exc.status_code >= 500 and attempt < 4:
                await asyncio.sleep(5 * (attempt + 1))
            else:
                raise

        except anthropic.APIConnectionError:
            if attempt < 4:
                await asyncio.sleep(10 * (attempt + 1))
            else:
                raise

    raise RuntimeError("Max retries exceeded")


async def translate_batch(
    client: anthropic.AsyncAnthropic,
    batch: list[dict],
    sem: asyncio.Semaphore,
    rl: RateLimiter,
) -> list[dict]:
    """Translate a batch. Falls back to per-entry on failure."""
    async with sem:
        payload = [
            {"id": e["_id"], "definition_fr": e["definition_fr"]}
            for e in batch
        ]
        try:
            return await _api_call(client, payload, max_tokens=4096, rate_limiter=rl)
        except Exception:
            # Fallback: translate one entry at a time (sem already held)
            out = []
            for e in batch:
                try:
                    single = [{"id": e["_id"], "definition_fr": e["definition_fr"]}]
                    result = await _api_call(client, single, max_tokens=512, rate_limiter=rl)
                    out.extend(result)
                except Exception:
                    out.append({"id": e["_id"], "definition_en": ""})
            return out


async def translate_long(
    client: anthropic.AsyncAnthropic,
    entry: dict,
    sem: asyncio.Semaphore,
    rl: RateLimiter,
) -> dict:
    """Translate a single long entry with a larger token budget."""
    async with sem:
        payload = [{"id": entry["_id"], "definition_fr": entry["definition_fr"]}]
        try:
            result = await _api_call(client, payload, max_tokens=8192, rate_limiter=rl)
            return result[0]
        except Exception:
            return {"id": entry["_id"], "definition_en": ""}


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
        print("Set it with:  export ANTHROPIC_API_KEY=sk-ant-...", file=sys.stderr)
        sys.exit(1)

    # Load input
    print(f"Loading {INPUT_FILE} ...", flush=True)
    with INPUT_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    entries = data["entries"]

    # Assign stable internal IDs
    for i, e in enumerate(entries):
        e["_id"] = i

    # Load checkpoint if present
    done: dict[int, str] = {}
    if CHECKPOINT.exists():
        with CHECKPOINT.open(encoding="utf-8") as f:
            done = {int(k): v for k, v in json.load(f).items()}
        print(f"Resuming — {len(done):,} entries already translated", flush=True)

    # Partition work
    all_need  = [e for e in entries
                 if e["_id"] not in done and e.get("definition_fr", "").strip()]
    empty_ct  = sum(1 for e in entries if not e.get("definition_fr", "").strip())
    long_     = [e for e in all_need if len(e["definition_fr"]) > LONG_THRESHOLD]
    short_    = [e for e in all_need if len(e["definition_fr"]) <= LONG_THRESHOLD]

    print()
    print(f"  Total entries    : {len(entries):>7,}")
    print(f"  Empty defs       : {empty_ct:>7,}  (skipped)")
    print(f"  Already done     : {len(done):>7,}")
    print(f"  Long entries     : {len(long_):>7,}  (>{LONG_THRESHOLD} chars, processed individually)")
    print(f"  Short to translate: {len(short_):>6,}")
    print(f"  Total to translate: {len(all_need):>6,}")
    print()

    if all_need:
        client = anthropic.AsyncAnthropic()
        sem    = asyncio.Semaphore(MAX_CONCURRENT)
        rl     = RateLimiter(REQUESTS_PER_MIN)
        t0     = time.monotonic()
        completed = 0
        total     = len(all_need)

        def progress(extra: str = "") -> None:
            elapsed = time.monotonic() - t0
            rate    = completed / elapsed if elapsed > 0 else 0
            eta     = (total - completed) / rate if rate > 0 else 0
            pct     = 100 * completed / total
            print(
                f"\r  {completed:>6,}/{total:,}  {pct:5.1f}%  "
                f"{rate:5.0f}/s  ETA {eta:4.0f}s  {extra}   ",
                end="", flush=True,
            )

        def save_checkpoint() -> None:
            with CHECKPOINT.open("w", encoding="utf-8") as f:
                json.dump(done, f, ensure_ascii=False)

        # ── Short batches (concurrent) ─────────────────────────────────────
        if short_:
            batches = [short_[i:i + BATCH_SIZE] for i in range(0, len(short_), BATCH_SIZE)]
            print(
                f"Batch-translating {len(short_):,} short entries "
                f"in {len(batches):,} tasks "
                f"({MAX_CONCURRENT} concurrent workers) ...",
                flush=True,
            )
            tasks = [asyncio.create_task(translate_batch(client, b, sem, rl)) for b in batches]

            batches_done = 0
            for fut in asyncio.as_completed(tasks):
                results = await fut
                for r in results:
                    done[r["id"]] = r.get("definition_en", "")
                    completed += 1
                batches_done += 1
                progress()
                if batches_done % 50 == 0:
                    save_checkpoint()

        # ── Long entries (one at a time) ───────────────────────────────────
        if long_:
            print(f"\n\nProcessing {len(long_)} long entries individually ...", flush=True)
            long_tasks = [
                asyncio.create_task(translate_long(client, e, sem, rl))
                for e in long_
            ]
            for fut in asyncio.as_completed(long_tasks):
                r = await fut
                done[r["id"]] = r.get("definition_en", "")
                completed += 1
                progress("(long)")

        save_checkpoint()
        elapsed = time.monotonic() - t0
        print(f"\n\nTranslation complete in {elapsed:.0f}s  ({elapsed/60:.1f} min)", flush=True)

    # ── Build output ──────────────────────────────────────────────────────────
    print("\nWriting output ...", flush=True)
    for e in entries:
        e["definition_en"] = done.get(e["_id"], "")
        del e["_id"]

    data["_metadata"].update({
        "has_english_translations":  True,
        "translation_model":         MODEL,
        "translation_date":          "2026-03-28",
        "translator_note": (
            "Machine translation via Anthropic Claude (claude-haiku-4-5). "
            "Nahuatl vocabulary preserved untranslated. "
            "Human review recommended for scholarly publication."
        ),
    })

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Remove checkpoint on success
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()

    # Final report
    size_mb     = OUTPUT_FILE.stat().st_size / 1_048_576
    filled      = sum(1 for e in entries if e.get("definition_en"))
    print(f"\n{OUTPUT_FILE}  ({size_mb:.1f} MB)")
    print(f"Entries with English translation: {filled:,} / {len(entries):,}")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
