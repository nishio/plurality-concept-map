#!/usr/bin/env python
import os, re, json, argparse, csv, hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from llm import ChatCompletionsClient
from prompts import SECTION_CONCEPTS_PROMPT, SECTION_RELATIONS_PROMPT
from utils import normalize_label, extract_json_block, slugify_id

def truncate_evidence(text: str, max_len: int = 200) -> str:
    """Truncate long evidence text, keeping start and end"""
    if len(text) <= max_len:
        return text
    half = max_len // 2 - 5
    return f"{text[:half]}...{text[-half:]}"

RELATION_TYPES = [
    "is_a", "part_of", "prerequisite_of", "example_of",
    "contrasts_with", "parameter_of", "returns", "uses"
]

@dataclass
class Evidence:
    text: str

@dataclass
class Concept:
    id: str
    label: str
    aliases: List[str] = field(default_factory=list)
    tier: str = "core"  # core|supplementary|advanced
    definition: Optional[str] = None
    evidence: List[Evidence] = field(default_factory=list)
    section_id: Optional[str] = None

@dataclass
class Edge:
    source: str
    target: str
    type: str
    confidence: float = 0.7
    evidence: List[Evidence] = field(default_factory=list)
    section_id: Optional[str] = None

@dataclass
class Section:
    id: str
    chapter: str
    title: str
    text: str
    path: str

def read_markdown_files(input_dir: Path) -> List[Tuple[str, str]]:
    files = sorted([p for p in input_dir.glob("**/*.md") if p.is_file()])
    items = []
    for p in files:
        items.append((str(p), p.read_text(encoding="utf-8", errors="ignore")))
    return items

def split_sections(md_text: str, segment_level: str = "h2") -> List[Tuple[str, str]]:
    level_map = {"h1": r"^# ", "h2": r"^## ", "h3": r"^### "}
    pattern = re.compile(level_map.get(segment_level, r"^## "), re.M)
    positions = [m.start() for m in pattern.finditer(md_text)]
    if not positions:
        return [("Whole", md_text)]
    sections = []
    positions.append(len(md_text))
    for i in range(len(positions) - 1):
        start, end = positions[i], positions[i+1]
        chunk = md_text[start:end].strip()
        first_line = chunk.splitlines()[0].lstrip("# ").strip()
        body = "\n".join(chunk.splitlines()[1:]).strip()
        sections.append((first_line or "Untitled", body))
    return sections

def dedupe_concepts(concepts: List[Concept]) -> List[Concept]:
    by_key: Dict[str, Concept] = {}
    def all_keys(c: Concept):
        labels = [c.label] + c.aliases
        return {normalize_label(x) for x in labels if x}
    for c in concepts:
        keys = all_keys(c)
        hit_key = None
        for k in keys:
            if k in by_key:
                hit_key = k
                break
        if hit_key is None:
            canon_key = normalize_label(c.label) if c.label else hashlib.md5(c.id.encode()).hexdigest()
            by_key[canon_key] = c
        else:
            base = by_key[hit_key]
            base.aliases = sorted(list(set(base.aliases + c.aliases + [c.label])))
            base.evidence.extend(c.evidence)
            tier_rank = {"core": 3, "supplementary": 2, "advanced": 1}
            if tier_rank.get(c.tier, 0) > tier_rank.get(base.tier, 0):
                base.tier = c.tier
            if not base.definition and c.definition:
                base.definition = c.definition
    out = []
    seen = set()
    for key, c in by_key.items():
        cid = slugify_id(c.label) or ("c_" + hashlib.md5(key.encode()).hexdigest()[:8])
        if cid in seen:
            cid = cid + "_" + hashlib.md5(key.encode()).hexdigest()[:4]
        seen.add(cid)
        c.id = cid
        out.append(c)
    return out

def filter_edges(edges: List[Edge], node_ids: set) -> List[Edge]:
    out = []
    for e in edges:
        if e.type not in RELATION_TYPES: 
            continue
        if e.source in node_ids and e.target in node_ids and e.source != e.target:
            out.append(e)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="contents/japanese", help="Markdown directory")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--segment-level", default="h2", choices=["h1","h2","h3"])
    ap.add_argument("--max-concepts", type=int, default=15)
    ap.add_argument("--cross-section", type=str, default="false", help="true/false")
    ap.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    args = ap.parse_args()

    input_dir = Path(args.input)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    client = ChatCompletionsClient(model=args.model)

    all_concepts: List[Concept] = []
    all_edges: List[Edge] = []
    sections: List[Section] = []

    files = read_markdown_files(input_dir)
    for idx, (path, txt) in enumerate(files, start=1):
        chapter = Path(path).name
        chunks = split_sections(txt, args.segment_level)
        for j, (title, body) in enumerate(chunks, start=1):
            sec_id = f"s{idx:02d}_{j:02d}"
            sec = Section(id=sec_id, chapter=chapter, title=title, text=body, path=path)
            sections.append(sec)

    for sec in sections:
        prompt = SECTION_CONCEPTS_PROMPT.format(
            section_title=sec.title,
            chapter=sec.chapter,
            max_concepts=args.max_concepts,
            text=sec.text[:12000]
        )
        txt = client.complete(prompt, expect_json=True)
        data = extract_json_block(txt) or {"concepts":[]}
        concepts = []
        for c in data.get("concepts", []):
            label = c.get("label","").strip()
            if not label: 
                continue
            concept = Concept(
                id=slugify_id(label) or ("tmp_"+hashlib.md5(label.encode()).hexdigest()[:8]),
                label=label,
                aliases=c.get("aliases",[]) or [],
                tier=c.get("tier","core"),
                definition=c.get("definition"),
                evidence=[Evidence(text=e.get("text","")) for e in c.get("evidence",[]) if e.get("text")],
                section_id=sec.id
            )
            concepts.append(concept)

        concept_labels = [c.label for c in concepts]
        rprompt = SECTION_RELATIONS_PROMPT.format(
            section_title=sec.title,
            chapter=sec.chapter,
            relation_types=", ".join(RELATION_TYPES),
            concepts=json.dumps(concept_labels, ensure_ascii=False, indent=2),
            text=sec.text[:12000]
        )
        rtxt = client.complete(rprompt, expect_json=True)
        print(f"Relations response for {sec.title}: {rtxt[:500]}...")
        rdata = extract_json_block(rtxt) or {"edges":[]}
        edges = []
        for e in rdata.get("edges", []):
            src = slugify_id(e.get("source_label",""))
            tgt = slugify_id(e.get("target_label",""))
            etype = e.get("type","")
            if not (src and tgt and etype):
                continue
            edge = Edge(
                source=src, target=tgt, type=etype,
                confidence=float(e.get("confidence",0.7)),
                evidence=[Evidence(text=x.get("text","")) for x in e.get("evidence",[]) if x.get("text")],
                section_id=sec.id
            )
            edges.append(edge)

        all_concepts.extend(concepts)
        all_edges.extend(edges)

    merged_concepts = dedupe_concepts(all_concepts)
    node_ids = {c.id for c in merged_concepts}
    filtered_edges = filter_edges(all_edges, node_ids)

    with (out_dir := Path(args.out)).joinpath("nodes.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id","label","tier","definition","aliases","evidence"])
        for c in merged_concepts: 
            evidence_texts = [truncate_evidence(e.text) for e in c.evidence]
            w.writerow([c.id, c.label, c.tier, (c.definition or ""), "|".join(c.aliases), "|".join(evidence_texts)])

    with (out_dir / "edges.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["source","target","type","confidence","evidence"])
        for e in filtered_edges: 
            evidence_texts = [truncate_evidence(ev.text) for ev in e.evidence]
            w.writerow([e.source, e.target, e.type, f"{e.confidence:.2f}", "|".join(evidence_texts)])

    graph = {
        "nodes": [
            {
                "id": c.id, 
                "label": c.label, 
                "tier": c.tier, 
                "definition": c.definition, 
                "aliases": c.aliases,
                "evidence": [{"text": e.text} for e in c.evidence]
            } for c in merged_concepts
        ],
        "edges": [
            {
                "source": e.source, 
                "target": e.target, 
                "type": e.type, 
                "confidence": e.confidence,
                "evidence": [{"text": ev.text} for ev in e.evidence]
            } for e in filtered_edges
        ]
    }
    Path(args.out,"graph.json").write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["```mermaid","graph TD"]
    for c in merged_concepts:
        if c.tier == "core": lines.append(f'  {c.id}["{c.label}"]')
    for e in filtered_edges:
        if e.type in ("prerequisite_of","is_a"): lines.append(f"  {e.source} -->|{e.type}| {e.target}")
    lines.append("```")
    Path(args.out,"mermaid.md").write_text("\n".join(lines), encoding="utf-8")

    # Generate both viewers
    viewer = (Path(__file__).parent / "viewer.html").read_text(encoding="utf-8")
    viewer = viewer.replace("/*__GRAPH_JSON__*/", json.dumps(graph, ensure_ascii=False))
    Path(args.out,"viewer.html").write_text(viewer, encoding="utf-8")
    
    # Enhanced viewer
    enhanced_viewer = (Path(__file__).parent / "viewer_enhanced.html").read_text(encoding="utf-8")
    enhanced_viewer = enhanced_viewer.replace("/*__GRAPH_JSON__*/", json.dumps(graph, ensure_ascii=False))
    Path(args.out,"viewer_enhanced.html").write_text(enhanced_viewer, encoding="utf-8")

    print(f"Done. Outputs saved under: {args.out}")

if __name__ == "__main__":
    main()
