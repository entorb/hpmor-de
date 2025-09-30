"""LLM/AI review of the translation."""  # noqa: INP001

import logging
import time
from pathlib import Path

from ai_llm_provider import (
    create_llm_provider,
    llm_call,
)

CHAPTER = 95

# Logging format: log level names to single letters
logging.addLevelName(logging.DEBUG, "D:")
logging.addLevelName(logging.INFO, "  ")
logging.addLevelName(logging.WARNING, "W:")
logging.addLevelName(logging.ERROR, "E:")
logging.addLevelName(logging.CRITICAL, "C:")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger()  # base logger without name

# LLM_PROVIDER, MODEL = ("Ollama", "llama3.2:1b")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-lite")
LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-pro")

MAX_LINES_PER_LLM_CALL = 200
GLOSSARY = Path("chapters/0woerterbuch.csv").read_text(encoding="utf-8")


def read_latest_prompt_from_file() -> str:
    """Read last section from 0prompts.md."""
    s = Path("scripts/ai_prompts.md").read_text(encoding="utf-8")
    # Find the last occurrence of "\n## " and get only the lines after it
    idx = s.rfind("\n## ")
    assert idx != -1, "Could not find last ## section in 0prompts.md"
    s = s[idx + 1 :]  # skip the newline before ##
    s = "\n".join(s.splitlines()[1:])  # skip the "## ..." header line itself
    s = s.strip()
    return s


INSTRUCTION = read_latest_prompt_from_file()
# INSTRUCTION = f"{read_latest_prompt_from_file()}\n- use this Glossary:\n{GLOSSARY}"


def split_into_chunks(lines: list[str], max_lines: int) -> list[str]:
    """Split list of lines to chunks of max_lines length."""
    chunks = []
    n = len(lines)
    i = 0
    while i < n:
        end = min(i + max_lines, n)
        chunk = lines[i:end]
        # Find last empty line in chunk to split more naturally
        split_idx = None
        for j in range(len(chunk) - 1, -1, -1):
            if chunk[j].strip() == "":
                split_idx = j + 1
                break
        if split_idx is not None and split_idx != 0:
            chunk_lines = chunk[:split_idx]
            next_i = i + split_idx
        else:
            chunk_lines = chunk
            next_i = end
        chunks.append("\n".join(chunk_lines))
        i = next_i
    return chunks


def review_chapter(chapter_no: int) -> None:
    """Read chapter, split into chunks, review chunks by LLM."""
    p = Path("chapters") / f"hpmor-chapter-{chapter_no:03}.tex"
    logger.info("# %s", p.name)
    cont_raw = p.read_text(encoding="utf-8")
    count_chars_total = len(cont_raw)
    cont = cont_raw.split("\n")
    del cont_raw
    count_lines_total = len(cont)
    logger.info("%d lines, %d chars.", count_lines_total, count_chars_total)
    chunks_in = split_into_chunks(cont, MAX_LINES_PER_LLM_CALL)

    chunks_out: list[str] = []
    time_start = time.time()
    tokens_used_total = 0
    retries_max = 3

    for chunk_no in range(len(chunks_in)):
        chunk_out = ""
        for retry_no in range(retries_max):
            if retry_no > 0:
                print(f"WARN: no comments, retry ({retry_no + 1}/{retries_max})")

            chunk_in = chunks_in[chunk_no]
            count_chunk_char = len(chunk_in)
            logger.info(
                "## %d/%d: %d lines, %d char",
                chunk_no + 1,
                len(chunks_in),
                len(chunk_in.split("\n")),
                count_chunk_char,
            )
            # recreate llm for each chunk speeds-up processing
            #  by dropping the old contents
            llm_provider = create_llm_provider(
                provider_name=LLM_PROVIDER, model=MODEL, instruction=INSTRUCTION
            )

            time_start_chunk = time.time()

            # here the AI magic happens
            chunk_out, tokens_used = llm_call(llm_provider, chunk_in)
            tokens_used_total += tokens_used

            logger.info("in %ds", (time.time() - time_start_chunk))

            # manually delete the llm to free resources
            del llm_provider

            # break the retry logic
            if "\n% " in chunk_out:
                break

        chunks_out.append(chunk_out)

    # Write the AI output to a new file
    p.with_suffix(".ai.tex").write_text(("\n".join(chunks_out)), encoding="utf-8")
    time_total = round(time.time() - time_start)
    logger.info(
        "%d lines reviewed in %ds, %d char/s, %.1f token/char",
        count_lines_total,
        time_total,
        (count_chars_total / time_total),
        (count_chars_total / tokens_used_total),
    )


if __name__ == "__main__":
    logger.info("%s %s", LLM_PROVIDER, MODEL)
    # review_chapter(CHAPTER)

    for i in range(95, 7, -1):
        p = (Path("chapters") / f"hpmor-chapter-{i:03}.tex").with_suffix(".ai.tex")
        if p.is_file():
            logger.info("skipping %s", p.name)
            continue

        logger.info("")
        try:
            review_chapter(i)
            logger.info("Sleeping for 5min")
            time.sleep(300)
        except Exception as e:
            logger.exception("Exception caught")
            # Gemini quota exceeded
            if "You exceeded your current quota" in str(e):
                raise
