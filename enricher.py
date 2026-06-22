import re
from typing import Dict, List
from config import VeanConfig


def clean_content(text: str) -> str:
    text = re.sub(r'inst\._@\.\S+?\b', 'inst', text)
    text = re.sub(r'_hygCtx\._hyg\.\d+', '', text)
    text = re.sub(r'\.\d{8,}\.', '.', text)
    return text


def extract_dependencies(proof_text: str, thm_name: str, noise_prefixes: List[str]) -> List[str]:
    all_deps = set(re.findall(r'\b[A-Z][a-zA-Z0-9_]*\.[a-zA-Z0-9_.]+\b', proof_text))
    return sorted([
        dep for dep in all_deps
        if not dep.startswith(tuple(noise_prefixes)) and dep != thm_name
    ])


def enrich_entry(raw: Dict, config: VeanConfig) -> Dict:
    thm_name = raw['name']
    raw_proof = raw.get('proof', '')
    proposition = raw.get('proposition', '')
    docstring = raw.get('docstring', '')

    deps = extract_dependencies(raw_proof, thm_name, config.extraction.noise_prefixes)

    semantic_text = f"Name: {thm_name}. "
    if docstring:
        semantic_text += f"Doc: {docstring} "
    semantic_text += f"Proposition: {proposition} "
    if deps:
        semantic_text += f"Dependencies: [{', '.join(deps)}]"

    semantic_text = clean_content(semantic_text)

    max_c = config.content.max_content_size
    max_f = config.content.max_field_size

    if len(semantic_text) > max_c:
        semantic_text = semantic_text[:max_c] + "... [truncated]"
    if len(proposition) > max_f:
        proposition = proposition[:max_f] + "... [truncated]"
    if len(raw_proof) > max_f:
        raw_proof = raw_proof[:max_f] + "... [truncated]"

    return {
        "id": thm_name,
        "content": semantic_text,
        "metadata": {
            "module": raw.get('module', 'unknown'),
            "type": "theorem",
            "proposition": proposition,
            "proof": raw_proof,
        }
    }
