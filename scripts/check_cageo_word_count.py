from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SECTIONS_DIR = ROOT / "paper" / "sections"
MANUSCRIPT_PATH = ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.tex"

ABSTRACT_LIMIT = 300
BODY_LIMIT = 5500
KEYWORD_MIN = 1
KEYWORD_MAX = 6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check abstract, keyword, and main-body word-count limits for the C&G manuscript."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when any limit is exceeded.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_environment(text: str, name: str) -> str:
    match = re.search(
        rf"\\begin\{{{name}\}}(.*?)\\end\{{{name}\}}",
        text,
        flags=re.S,
    )
    if not match:
        raise ValueError(f"Could not extract {name} from manuscript")
    return match.group(1)


def strip_latex(text: str) -> str:
    text = re.sub(r"%.*", " ", text)
    text = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\\begin\{equation\*?\}.*?\\end\{equation\*?\}", " ", text, flags=re.S)
    text = re.sub(r"\$.*?\$", " ", text, flags=re.S)
    previous = None
    while previous != text:
        previous = text
        text = re.sub(
            r"\\[A-Za-z*]+(?:\[[^\]]*\])?\{([^{}]*)\}",
            r" \1 ",
            text,
        )
    text = re.sub(r"\\[A-Za-z@]+(?:\[[^\]]*\])?", " ", text)
    text = re.sub(r"[{}_^&~]", " ", text)
    return " ".join(text.split())


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*", text))


def keyword_count() -> int:
    manuscript = read_text(MANUSCRIPT_PATH)
    keywords = extract_environment(manuscript, "keywords")
    return len([part.strip() for part in keywords.split("\\sep") if part.strip()])


def abstract_word_count() -> int:
    abstract = read_text(SECTIONS_DIR / "abstract.tex")
    abstract_text = strip_latex(extract_environment(abstract, "abstract"))
    return count_words(abstract_text)


def body_word_count() -> int:
    body_files = [
        "introduction.tex",
        "related_work.tex",
        "method.tex",
        "experiments.tex",
        "conclusion.tex",
    ]
    text = "\n".join(strip_latex(read_text(SECTIONS_DIR / filename)) for filename in body_files)
    return count_words(text)


def main() -> None:
    args = parse_args()
    abstract_words = abstract_word_count()
    body_words = body_word_count()
    keywords = keyword_count()

    print(f"abstract_words: {abstract_words}")
    print(f"body_words: {body_words}")
    print(f"keywords: {keywords}")

    errors: list[str] = []
    if abstract_words > ABSTRACT_LIMIT:
        errors.append(
            f"Abstract exceeds {ABSTRACT_LIMIT} words: {abstract_words}"
        )
    if body_words > BODY_LIMIT:
        errors.append(
            f"Main body exceeds {BODY_LIMIT} words: {body_words}"
        )
    if not KEYWORD_MIN <= keywords <= KEYWORD_MAX:
        errors.append(
            f"Keyword count must be between {KEYWORD_MIN} and {KEYWORD_MAX}: {keywords}"
        )

    if errors:
        print("word_count_issues:")
        for item in errors:
            print(f"- {item}")
        if args.strict:
            sys.exit(1)
    else:
        print("word_count_issues: none")


if __name__ == "__main__":
    main()
