"""LLM/AI review of the translation."""  # noqa: INP001

from pathlib import Path
from time import time

from ai_llm_provider import GeminiProvider, OllamaProvider, OpenAIProvider, llm_call

CHAPTER = 95

# LLM_PROVIDER, MODEL = ("Ollama", "llama3.2:1b")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash-lite")
# LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-flash")
LLM_PROVIDER, MODEL = ("Gemini", "gemini-2.5-pro")

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
    print("# " + p.name)
    cont_raw = p.read_text(encoding="utf-8")
    count_chars_total = len(cont_raw)
    cont = cont_raw.split("\n")
    del cont_raw
    count_lines_total = len(cont)
    print(f"{count_lines_total} lines, {count_chars_total} chars.")
    chunks_in = split_into_chunks(cont, MAX_LINES_PER_LLM_CALL)

    chunks_out: list[str] = []
    time_start = time()
    tokens_used_total = 0

    for chunk_no in range(len(chunks_in)):
        chunk_in = chunks_in[chunk_no]
        count_chunk_char = len(chunk_in)
        print(
            f"## {chunk_no + 1}/{len(chunks_in)}: "
            f"{len(chunk_in.split('\n'))} lines, {count_chunk_char} char"
        )

        # try: recreate llm for each chunk to speed-up by dropping the contents
        if LLM_PROVIDER == "Ollama":
            llm_provider = OllamaProvider(instruction=INSTRUCTION, model=MODEL)
        elif LLM_PROVIDER == "OpenAI":
            llm_provider = OpenAIProvider(instruction=INSTRUCTION, model=MODEL)
        elif LLM_PROVIDER == "Gemini":
            llm_provider = GeminiProvider(instruction=INSTRUCTION, model=MODEL)
        else:
            msg = f"Unknown LLM {LLM_PROVIDER}"
            raise ValueError(msg)

        time_start_chunk = time()

        # here the AI magic happens
        chunk_out, tokens_used = llm_call(llm_provider, chunk_in)
        tokens_used_total += tokens_used

        print(f"in {round(time() - time_start_chunk)}s")
        chunks_out.append(chunk_out)

        # manually delete the llm to free resources
        del llm_provider

    # Write the AI output to a new file
    p.with_suffix(".ai.tex").write_text(("\n".join(chunks_out)), encoding="utf-8")
    time_total = round(time() - time_start)
    print(
        f"{count_lines_total} lines reviewed in {time_total}s,"
        f" {round(count_chars_total / time_total)} char/s,"
        f" {round(count_chars_total / tokens_used_total, 1)} token/char"
    )


if __name__ == "__main__":
    print()
    print(LLM_PROVIDER, MODEL)
    review_chapter(CHAPTER)
