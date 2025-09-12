SECTION_CONCEPTS_PROMPT = """
You are given a section from a textbook chapter.

Task: extract up to {max_concepts} key **knowledge concepts** that are central for learning (NOT trivia).
Return STRICT JSON with this schema:
{{
  "concepts": [{{ 
      "label": str,                    # canonical short name
      "aliases": [str],                # synonyms / code tokens etc.
      "definition": str,               # <= 30 words plain definition
      "evidence": [{{"text": str}}]    # short quotes from the section
  }}]
}}

Rules:
- Focus on curriculum-aligned concepts that are central for learning.
- Avoid meta, anecdotes, history unless explicitly in objectives.
- Use short labels, no markdown.
- **CRITICAL: Language matching requirement**
  - If source text is in Japanese: ALL labels and definitions MUST be in Japanese
  - Only use English if the exact English term appears in the original Japanese text (e.g., "AI", "Plurality")
  - When Japanese text discusses English concepts, prefer Japanese translations when they exist in the text
  - Example: If text says "デジタル民主主義", use "デジタル民主主義" not "Digital Democracy"
- Evidence must be *verbatim* spans inside the section.

Section title: {section_title}
Chapter file: {chapter}
---
{{
{text}
}}
"""

SECTION_RELATIONS_PROMPT = """
You are given a list of concept labels and the same section text.
Task: propose relations BETWEEN THESE CONCEPTS ONLY, as a list of edges.

Return STRICT JSON with:
{{
  "edges": [{{ 
    "source_label": str, 
    "target_label": str, 
    "relation": str,               # short label for graph display (1-3 words)
    "relation_description": str,   # full natural language description
    "confidence": float,           # 0.0-1.0
    "evidence": [{{"text": str}}]  # short quotes from the section
  }}]
}}

Rules:
- Only connect the provided concepts. No new nodes.
- For "relation": provide a short label (1-3 words) suitable for graph display (e.g., "includes", "type of", "requires").
- For "relation_description": provide full natural language description that includes the target concept (e.g., "Logistic regression is a type of machine learning").
- **CRITICAL: Language matching requirement**
  - If source text is in Japanese: ALL relation and relation_description MUST be in Japanese
  - Only use English if the exact English term appears in the original Japanese text
  - Japanese examples: relation: "含む", "要求する", "影響する"; relation_description: "Aは〜を含む", "Bは〜を要求する"
  - Ensure natural Japanese phrasing in relation_description
- Evidence must ground the relation; omit the edge if no textual support.
- Keep 3-12 edges per section.

Concepts:
{concepts}

Section title: {section_title}
Chapter file: {chapter}
---
{{
{text}
}}
"""
