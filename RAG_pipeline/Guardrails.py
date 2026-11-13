"""
    There are three checkpoints:
      1. check_input() before retrieval (user query)
      2. filter_context() after retrieval (retrieved chunks)
      3. check_output() after generation (LLM answer)
"""

import re 

MAX_QUERY_CHARS = 500 
BLOCK_MESSAGE = "Sorry, I can't  process this request"

# prompt injection 
INJECTION_PARTTERNS = [
    r"ignore (all | any | the)? (previous|prior|above|earlier) (instructions|prompts?|rules)",
    r"disregared .{0, 40}(instructions|rules|prompt)",
    r"forget (everything|all|your) .{0,30}(instructions|rules|above)",
    r"(reveal|show|print|repeat|display|leak) .{0, 40}(system prompt|hidden prompt|instructions|api key)",
    r"you are now\b",
    r"pretend (to be |you are)",
    r"\b(jailbreask|developer mode|DAN mode)\b",
    r"override .{0, 30}(rules | instructions | safety | guardrails?)",
    r"new instructions?:",
    r"<\s*/?\s*(system|assistant)\s*>",
]
_INJECTION_RE = [re.compile(p, re.IGNORECASE) for p in INJECTION_PARTTERNS]


# Personally Identifiable Information patterns (indai-foused + generic)
PII_PATTERNS = {
    "EMAIL": re.compile(r"[\w.+-]+@[\w-]+.[w.-]+"),
    "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
    "AADHAAR": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "CARD": re.compile(r"\b(?:\d[ -]?){13, 16}\b"),
    "PHONE": re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")
}

# Text that shoudl never appear in an answer (system prompt leakage)
LEAK_MARKERS = [
    "you are a helpful financial assitant", 
    "using only the context below",
    "pinecone_api_key",
    "groq_api_key",
]

def _has_injection(text):
    return any(p.search(text) for p in _INJECTION_RE)

def mask_pii(text):
    for label, pattern in PII_PATTERNS.items():
        text = pattern.sub(f"[{label} REMOVED]", text)
    return text


#1. Input Guard (before retrieval)
def check_input(query):
    """Returns (is_ok, query_or_message)."""
    query = (query or "").strip()
    if not query:
        return False, "Please enter a question."
    if len(query) > MAX_QUERY_CHARS:
        return False, f"Query too long (max {MAX_QUERY_CHARS} characters)."
    if _has_injection(query):
        return False, BLOCK_MESSAGE
    return True, mask_pii(query) 


#2. Context guard (after retrieval)
def filter_context(docs):
    """Drop retrieved chunks that contain hidden instructions (indirect injection)."""
    return [d for d in docs if not _has_injection(d.page_content)]

#3. Output guard (after generation)
def check_output(answer):
    """Returns a safe answer string."""
    lowered = answer.lower()
    if any(marker in lowered for marker in LEAK_MARKERS):
        return BLOCK_MESSAGE
    return mask_pii(answer)

# print("Everthing is working correct!")