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
- Use the original language of the text: if the source text is in Japanese, use Japanese labels and definitions. Only use English for terms that appear in English in the original text.
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
    "relation": str,               # natural language description of the relationship
    "confidence": float,           # 0.0-1.0
    "evidence": [{{"text": str}}]  # short quotes from the section
  }}]
}}

Rules:
- Only connect the provided concepts. No new nodes.
- Express relationships using natural language that includes the target concept (e.g., "Logistic regression is a type of machine learning").
- Use the original language of the text: if the source text is in Japanese, use Japanese relation descriptions. Only use English for terms that appear in English in the original text.
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
