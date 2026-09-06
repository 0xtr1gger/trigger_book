#!/usr/bin/env python3
"""
lint_vault.py - Deterministic linter for Obsidian cybersecurity vault notes.

Validates notes against .editorial/policy/ rules:
- Banned AI vocabulary and fluff words
- Dangling participle clauses (-ing tails)
- Heading sentence casing and gerund forms
- Backticked wikilinks (`[[Link]]`)
- Missing code block languages and shell prompts in code
- Conversational intros/outros
- Markdown links pointing to internal markdown files
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, NamedTuple

class Violation(NamedTuple):
    line_num: int
    rule_id: str
    category: str  # STYLE, FORMAT, TECH, STRUCTURE
    message: str
    line_content: str

# Common technical acronyms / proper nouns exempt from heading sentence case checks
EXEMPT_PROPER_NOUNS = {
    "AD", "DC", "DACL", "SACL", "ACL", "ACE", "SID", "SMB", "RPC", "SCM", "CVE",
    "OS", "IP", "FQDN", "API", "DLL", "CIM", "WMI", "PEAS", "SAMR", "LDAP",
    "KERBEROS", "NTLM", "LSASS", "SAM", "SYSTEM", "UAC", "RBCD", "AS-REP",
    "TGT", "TGS", "SPN", "KDC", "GPO", "LAPS", "SYSVOL", "EOP", "LPE", "RCE",
    "MSFVENOM", "MIMIKATZ", "RUBEUS", "CERTIPY", "NETEXEC", "IMPACKET",
    "WINDOWS", "LINUX", "POWERSHELL", "CMD", "BASH", "PYTHON", "AZURE", "ENTRA",
    "DEFENDER", "EDR", "AV", "AMSI", "ETW", "BYOVD", "HVCI", "VBS", "SMEP", "SMAP",
    "OBSIDIAN", "GITHUB", "GIT", "MICROSOFT", "ACTIVE", "DIRECTORY", "QUARTZ"
}

BANNED_WORDS = [
    (r"\bunder the hood\b", "Conversational cliché: 'under the hood' is banned. State direct OS behavior."),
    (r"\bin a nutshell\b", "Conversational cliché: 'in a nutshell' is banned. State facts directly."),
    (r"\bat its core\b", "Conversational cliché: 'at its core' is banned."),
    (r"\bcrucial\b", "AI buzzword: 'crucial' is banned. State the technical consequence instead."),
    (r"\bessential\b", "AI buzzword: 'essential' is banned. State the technical prerequisite."),
    (r"\bpivotal\b", "AI buzzword: 'pivotal' is banned."),
    (r"\bvital\b", "AI buzzword: 'vital' is banned."),
    (r"\bleverage\b", "Corporate buzzword: 'leverage' is banned. Use 'use', 'abuse', or 'exploit'."),
    (r"\butilize\b", "Pseudo-formal filler: 'utilize' is banned. Use 'use'."),
    (r"\bdelve\b", "AI signature word: 'delve' is banned."),
    (r"\bharness\b", "AI signature word: 'harness' is banned."),
    (r"\bseamlessly\b", "AI buzzword: 'seamlessly' is banned."),
    (r"\brobust\b", "Marketing fluff: 'robust' is banned. Describe specific capabilities."),
    (r"\bbasically\b", "Patronizing filler: 'basically' is banned. Remove."),
    (r"\bsimply\b", "Patronizing filler: 'simply' is banned. Remove."),
    (r"\bobviously\b", "Patronizing filler: 'obviously' is banned. Remove."),
    (r"\bclearly\b", "Patronizing filler: 'clearly' is banned. Remove.")
]

DANGLING_PARTICIPLES = [
    (r",\s*allowing\s+(?:you|an?\s+attacker|a\s+user)\s+to\b", "Dangling participle tail: replace ', allowing...' with a direct cause-and-effect sentence."),
    (r",\s*leading\s+to\b", "Dangling participle tail: replace ', leading to...' with direct cause-and-effect."),
    (r",\s*resulting\s+in\b", "Dangling participle tail: replace ', resulting in...' with direct cause-and-effect."),
    (r",\s*enabling\s+(?:you|an?\s+attacker|a\s+user|unauthenticated)\b", "Dangling participle tail: replace ', enabling...' with direct cause-and-effect."),
    (r",\s*granting\s+(?:you|SYSTEM|administrator)\b", "Dangling participle tail: replace ', granting...' with direct cause-and-effect.")
]

CONVERSATIONAL_INTROS = [
    (r"^\s*In this (?:guide|section|article|note),?\s+(?:we will|you will|we'll)\b", "Conversational intro: jump straight to facts or Scope callout."),
    (r"^\s*Welcome to\b", "Conversational intro: greetings are forbidden."),
    (r"^\s*Hope this helps\b", "Conversational outro: sign-offs are forbidden."),
    (r"^\s*As (?:we have seen|previously discussed|you can see)\b", "Meta-commentary filler is forbidden.")
]

def check_heading_sentence_case(heading_text: str) -> List[str]:
    """Flag words in headings that appear to be Title Case instead of sentence case."""
    # Strip markdown symbols
    cleaned = re.sub(r"^#+\s*", "", heading_text).strip()
    words = re.findall(r"[A-Za-z0-9_]+", cleaned)
    if not words:
        return []
    
    issues = []
    # First word can be capitalized; subsequent words should be lowercase unless exempt
    for w in words[1:]:
        if w[0].isupper() and w.upper() not in EXEMPT_PROPER_NOUNS:
            # Check if it's all uppercase (acronym)
            if not w.isupper():
                issues.append(f"Word '{w}' in heading '{cleaned}' should be lowercase (sentence case).")
    return issues

def lint_file(file_path: Path, active_categories: set) -> List[Violation]:
    violations: List[Violation] = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [Violation(0, "IO_ERR", "TECHNICAL", f"Failed to read file: {e}", "")]

    lines = content.splitlines()
    in_frontmatter = False
    in_code_block = False
    code_block_lang = ""

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Frontmatter detection
        if idx == 1 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
            continue

        # Code block tracking
        if stripped.startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_lang = stripped[3:].strip()
                if "FORMAT" in active_categories and not code_block_lang:
                    violations.append(Violation(
                        idx, "F001", "FORMAT",
                        "Code block missing language tag (e.g., ```powershell, ```bash, ```cmd).",
                        line
                    ))
            else:
                in_code_block = False
                code_block_lang = ""
            continue

        # Content inside code block
        if in_code_block:
            if "FORMAT" in active_categories:
                if re.match(r"^\s*(?:PS\s+[A-Za-z]:\\.*?>|[A-Za-z]:\\.*?>|\$\s+)\S+", line):
                    violations.append(Violation(
                        idx, "F002", "FORMAT",
                        "Code block contains shell prompt (e.g. 'PS C:\\>', 'C:\\>'). Keep commands clean and copy-pastable.",
                        line
                    ))
            continue

        # Markdown headings checks
        if stripped.startswith("#"):
            heading_title = re.sub(r"^#+\s*", "", stripped)
            
            # Check banned word "Mechanics" in heading
            if "STYLE" in active_categories:
                if re.search(r"\bmechanics\b", heading_title, re.IGNORECASE):
                    violations.append(Violation(
                        idx, "S001", "STYLE",
                        "Heading contains banned term 'mechanics'. Use 'How [Vector] works' or 'Security model'.",
                        line
                    ))
            
            # Check sentence case in headings
            if "FORMAT" in active_categories:
                case_issues = check_heading_sentence_case(stripped)
                for issue in case_issues:
                    violations.append(Violation(idx, "F003", "FORMAT", issue, line))
            continue

        # Backticked wikilinks: `[[...]]`
        if "FORMAT" in active_categories:
            if re.search(r"`\[\[.*?\]\]`", line):
                violations.append(Violation(
                    idx, "F004", "FORMAT",
                    "Wikilink enclosed in backticks (`[[...]]`). Wikilinks must never have backticks.",
                    line
                ))

        # Markdown links pointing to internal markdown files instead of wikilinks
        if "FORMAT" in active_categories:
            if re.search(r"\[([^\]]+)\]\((?:\.\.?\/|content\/)[^)]+\.md\)", line):
                violations.append(Violation(
                    idx, "F005", "FORMAT",
                    "Internal documentation link uses Markdown link [text](path.md) instead of Obsidian wikilink [[...]].",
                    line
                ))

        # Banned vocabulary
        if "STYLE" in active_categories:
            for pattern, msg in BANNED_WORDS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(Violation(idx, "S002", "STYLE", msg, line))

        # Dangling participles
        if "STYLE" in active_categories:
            for pattern, msg in DANGLING_PARTICIPLES:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(Violation(idx, "S003", "STYLE", msg, line))

        # Conversational intros / outros
        if "STYLE" in active_categories:
            for pattern, msg in CONVERSATIONAL_INTROS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(Violation(idx, "S004", "STYLE", msg, line))

        # Reader perspective: check for 'the attacker runs'
        if "STYLE" in active_categories:
            if re.search(r"\b(?:the|an)\s+attacker\s+(?:can\s+run|runs|executes|must)\b", line, re.IGNORECASE):
                violations.append(Violation(
                    idx, "S005", "STYLE",
                    "Address reader as 'you' for instructions rather than 'the attacker'.",
                    line
                ))

    return violations

def main():
    parser = argparse.ArgumentParser(description="Deterministic Obsidian Vault Linter")
    parser.add_argument("files", nargs="*", help="Files or directories to lint")
    parser.add_argument("--check", choices=["all", "style", "formatting"], default="all",
                        help="Filter which category of checks to run (default: all)")
    args = parser.parse_args()

    if not args.files:
        print("Usage: lint_vault.py <file1.md> [file2.md...] or specify paths")
        sys.exit(0)

    categories = {"STYLE", "FORMAT", "TECHNICAL", "STRUCTURE"}
    if args.check == "style":
        categories = {"STYLE"}
    elif args.check == "formatting":
        categories = {"FORMAT"}

    total_violations = 0
    files_to_check = []

    for f in args.files:
        p = Path(f)
        if p.is_file() and p.suffix == ".md":
            files_to_check.append(p)
        elif p.is_dir():
            files_to_check.extend(p.glob("**/*.md"))

    if not files_to_check:
        print("No markdown files found to lint.")
        sys.exit(0)

    for file_path in files_to_check:
        violations = lint_file(file_path, categories)
        if violations:
            total_violations += len(violations)
            print(f"\n\033[1;36m==> {file_path}\033[0m ({len(violations)} issues)")
            for v in violations:
                color = "\033[33m" if v.category == "STYLE" else "\033[35m"
                print(f"  \033[1mLine {v.line_num:4d}\033[0m: [{color}{v.category}-{v.rule_id}\033[0m] {v.message}")
                print(f"            \033[2m{v.line_content.strip()[:100]}\033[0m")

    print("\n" + "=" * 60)
    if total_violations == 0:
        print(f"\033[32m[✓] All {len(files_to_check)} files passed linting with zero issues.\033[0m")
        sys.exit(0)
    else:
        print(f"\033[31m[✗] Found {total_violations} issue(s) across {len(files_to_check)} file(s).\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
