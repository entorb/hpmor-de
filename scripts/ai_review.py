"""LLM/AI review of the translation."""  # noqa: INP001

import logging
import re
import time
from pathlib import Path

from ai_llm_provider import create_llm_provider

# Logging format: log level names to single letters
logging.addLevelName(logging.DEBUG, "D:")
logging.addLevelName(logging.INFO, "  ")
logging.addLevelName(logging.WARNING, "W:")
logging.addLevelName(logging.ERROR, "E:")
logging.addLevelName(logging.CRITICAL, "C:")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")  #  %(name)s
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger()  # base logger without name
logger.setLevel(logging.INFO)

# LLM_PROVIDER, MODEL = ("Ollama", "llama3.2:1b")
LLM_PROVIDER, MODEL = ("Mistral", "mistral-large-latest")
# LLM_PROVIDER, MODEL = ("Mistral", "mistral-medium-latest")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-lite")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-pro")
# LLM_PROVIDER, MODEL = ("AzureOpenAI", "gpt-5-nano")
# LLM_PROVIDER, MODEL = ("AzureOpenAI", "gpt-5-mini")
# LLM_PROVIDER, MODEL = ("AzureOpenAI", "gpt-5")

MAX_LINES_PER_LLM_CALL = 200
SKIP_COMMENTS = False


def _format_glossary(csv_text: str) -> str:
    """Parse glossary CSV and format it clearly for the LLM."""
    lines = []
    for row in csv_text.strip().splitlines():
        if not row.strip() or row.startswith(("==", "EN,DE")):
            continue
        parts = row.split(",", 1)
        if len(parts) == 2 and parts[0].strip() and parts[1].strip():  # noqa: PLR2004
            lines.append(f"  {parts[0].strip()} → {parts[1].strip()}")
    return "\n".join(lines)


GLOSSARY = _format_glossary(
    Path("chapters/0woerterbuch.csv").read_text(encoding="utf-8")
)


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


# INSTRUCTION = read_latest_prompt_from_file()
INSTRUCTION = f"{read_latest_prompt_from_file()}\n\n## Glossary\n{GLOSSARY}"


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


def _replace_comments_with_refs(lines: list[str]) -> tuple[list[str], dict[int, str]]:
    """
    Replace consecutive comment-line blocks with short reference placeholders.

    Each block of one or more comment lines (starting with ``%``) is replaced
    by a single line ``%@@REF:<n>@@`` so the LLM keeps it in place without
    being distracted by long comment text.

    Returns:
        result_lines: the lines with comment blocks replaced by refs.
        ref_map: mapping from ref number to the original comment block text.

    """
    result_lines: list[str] = []
    ref_map: dict[int, str] = {}
    ref_counter = 0
    pending_comments: list[str] = []

    for line in lines:
        if re.match(r"^\s*%", line):
            pending_comments.append(line)
        else:
            if pending_comments:
                ref_map[ref_counter] = "\n".join(pending_comments)
                result_lines.append(f"%@@REF:{ref_counter}@@")
                ref_counter += 1
                pending_comments = []
            result_lines.append(line)

    # trailing comment block
    if pending_comments:
        ref_map[ref_counter] = "\n".join(pending_comments)
        result_lines.append(f"%@@REF:{ref_counter}@@")

    return result_lines, ref_map


def _restore_comments_from_refs(lines: list[str], ref_map: dict[int, str]) -> list[str]:
    """
    Replace ``%@@REF:<n>@@`` placeholders back with the original comment blocks.

    Refs that the LLM dropped are appended at the end so no comments are lost.
    """
    result: list[str] = []
    restored_refs: set[int] = set()

    for line in lines:
        m = re.match(r"^\s*%@@REF:(\d+)@@\s*$", line)
        if m:
            ref_id = int(m.group(1))
            if ref_id in ref_map:
                result.append(ref_map[ref_id])
                restored_refs.add(ref_id)
            # silently drop unknown refs (shouldn't happen)
        else:
            result.append(line)

    # append any refs the LLM accidentally removed so nothing is lost
    for ref_id in sorted(ref_map.keys() - restored_refs):
        logger.warning("Comment ref %d was dropped by LLM, appending at end.", ref_id)
        result.append(ref_map[ref_id])

    return result


def review_chapter(chapter_no: int) -> None:
    """Read chapter, split into chunks, review chunks by LLM."""
    p = Path("chapters") / f"hpmor-chapter-{chapter_no:03}.tex"
    logger.info("# %s", p.name)
    cont_raw = p.read_text(encoding="utf-8")
    count_chars_total = len(cont_raw)
    cont = cont_raw.split("\n")
    comment_ref_map: dict[int, str] | None = None
    if SKIP_COMMENTS:
        cont, comment_ref_map = _replace_comments_with_refs(cont)
    del cont_raw
    count_lines_total = len(cont)
    logger.info("%d lines, %d chars.", count_lines_total, count_chars_total)
    chunks_in = split_into_chunks(cont, MAX_LINES_PER_LLM_CALL)

    chunks_out: list[str] = []
    time_start = time.time()
    tokens_used_total = 0
    retries_max = 1 if SKIP_COMMENTS else 3

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
            llm_provider = create_llm_provider(provider_name=LLM_PROVIDER)

            time_start_chunk = time.time()

            # here the AI magic happens
            chunk_out, tokens_used = llm_provider.call(MODEL, INSTRUCTION, chunk_in)
            tokens_used_total += tokens_used

            logger.info("in %ds", (time.time() - time_start_chunk))

            # manually delete the llm to free resources
            del llm_provider

            # break the retry logic if comments survived in the output, otherwise retry
            input_comment_count = sum(
                1 for ln in chunk_in.split("\n") if ln.lstrip().startswith("%")
            )
            output_comment_count = sum(
                1 for ln in chunk_out.split("\n") if ln.lstrip().startswith("%")
            )
            if (
                input_comment_count == 0
                or output_comment_count >= input_comment_count * 0.5
            ):
                break

        chunks_out.append(chunk_out)

        # Write progress after each chunk; restore refs only on final chunk
        output_text = "\n".join(chunks_out)
        if chunk_no == len(chunks_in) - 1 and comment_ref_map is not None:
            output_lines = output_text.split("\n")
            output_lines = _restore_comments_from_refs(output_lines, comment_ref_map)
            output_text = "\n".join(output_lines)

        # Write the AI output to a new file
        p.with_suffix(".ai.tex").write_text(output_text, encoding="utf-8")

    time_total = max(round(time.time() - time_start), 1)
    logger.info(
        "%d lines reviewed in %ds, %d tokens, %d char/s, %.1f token/char.",
        count_lines_total,
        time_total,
        tokens_used_total,
        (count_chars_total / time_total),
        (count_chars_total / max(tokens_used_total, 1)),
    )


if __name__ == "__main__":
    logger.info("LLM: %s, Model: %s", LLM_PROVIDER, MODEL)

    # # single chapter
    # review_chapter(27)
    # exit()

    # multiple chapters
    for i in range(40, 50):
        p = (Path("chapters") / f"hpmor-chapter-{i:03}.tex").with_suffix(".ai.tex")
        if p.is_file():
            logger.info("skipping %s", p.name)
            continue

        logger.info("")
        try:
            review_chapter(i)
            if LLM_PROVIDER == "Gemini":
                logger.info("Sleeping for 5min")
                time.sleep(300)
        except Exception as e:
            logger.exception("Exception caught")
            # Gemini quota exceeded
            if "You exceeded your current quota" in str(e):
                raise
