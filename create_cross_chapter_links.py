#!/usr/bin/env python3
"""
章間の関連概念リンクを発見するためのプロンプトを生成するスクリプト
"""
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re


def load_merged_graph(filepath: Path) -> Dict:
    """結合グラフを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_section_from_node(node: Dict) -> str:
    """ノードからセクションIDを抽出"""
    return node.get('source_section', '')


def group_nodes_by_section(graph: Dict) -> Dict[str, List[Dict]]:
    """ノードをセクション別にグループ化"""
    section_nodes = defaultdict(list)
    for node in graph['nodes']:
        section = extract_section_from_node(node)
        if section:
            section_nodes[section].append(node)
    return dict(section_nodes)


def find_similar_concepts(graph: Dict) -> List[Tuple[Dict, Dict, float]]:
    """類似概念のペアを見つける（異なるセクション間）"""
    similar_pairs = []
    nodes = graph['nodes']
    
    for i, node1 in enumerate(nodes):
        section1 = extract_section_from_node(node1)
        if not section1:
            continue
            
        for node2 in nodes[i+1:]:
            section2 = extract_section_from_node(node2)
            if not section2 or section1 == section2:
                continue
            
            # 類似度を計算（シンプルな文字列比較）
            label1 = node1.get('label', '').lower()
            label2 = node2.get('label', '').lower()
            original1 = node1.get('original_id', '').lower()
            original2 = node2.get('original_id', '').lower()
            
            # 完全一致（元のIDが同じ = 衝突解決されたペア）
            if original1 and original1 == original2:
                similar_pairs.append((node1, node2, 1.0))
            # 部分一致
            elif label1 in label2 or label2 in label1:
                similarity = min(len(label1), len(label2)) / max(len(label1), len(label2))
                if similarity > 0.7:  # 70%以上の類似度
                    similar_pairs.append((node1, node2, similarity))
    
    return sorted(similar_pairs, key=lambda x: x[2], reverse=True)


def analyze_concept_relationships(graph: Dict) -> Dict:
    """概念間の関係性を分析"""
    section_nodes = group_nodes_by_section(graph)
    similar_concepts = find_similar_concepts(graph)
    
    # セクション間の潜在的リンクを分析
    cross_section_links = defaultdict(list)
    
    for node1, node2, similarity in similar_concepts:
        section1 = extract_section_from_node(node1)
        section2 = extract_section_from_node(node2)
        
        link_info = {
            'from_section': section1,
            'from_concept': node1['label'],
            'from_id': node1['id'],
            'to_section': section2,
            'to_concept': node2['label'],
            'to_id': node2['id'],
            'similarity': similarity,
            'original_id_match': node1.get('original_id') == node2.get('original_id')
        }
        
        cross_section_links[section1].append(link_info)
        # 逆方向のリンクも追加
        reverse_link = {
            'from_section': section2,
            'from_concept': node2['label'],
            'from_id': node2['id'],
            'to_section': section1,
            'to_concept': node1['label'],
            'to_id': node1['id'],
            'similarity': similarity,
            'original_id_match': node1.get('original_id') == node2.get('original_id')
        }
        cross_section_links[section2].append(reverse_link)
    
    return {
        'section_nodes': section_nodes,
        'similar_concepts': similar_concepts,
        'cross_section_links': dict(cross_section_links)
    }


def create_link_discovery_prompt(analysis: Dict, target_section: str) -> str:
    """特定セクションの章間リンク発見用プロンプトを生成"""
    
    section_nodes = analysis['section_nodes']
    cross_links = analysis['cross_section_links'].get(target_section, [])
    
    # 現在のセクションの概念リスト
    current_concepts = section_nodes.get(target_section, [])
    current_concept_list = '\n'.join([f"- {node['label']}: {node.get('definition', '')}" 
                                     for node in current_concepts])
    
    # 他セクションの関連概念
    related_concepts_by_section = defaultdict(list)
    for link in cross_links:
        related_concepts_by_section[link['to_section']].append(link)
    
    related_sections_text = []
    for section, links in related_concepts_by_section.items():
        concepts = '\n'.join([f"  - {link['to_concept']} (類似度: {link['similarity']:.2f})"
                             for link in links])
        related_sections_text.append(f"セクション {section}:\n{concepts}")
    
    related_text = '\n\n'.join(related_sections_text)
    
    prompt = f"""# 章間概念リンクの発見と提案

## 現在のセクション: {target_section}

### このセクションの主要概念:
{current_concept_list}

### 他セクションの潜在的関連概念:
{related_text if related_text else "（自動検出された類似概念なし）"}

## タスク:

上記の情報を基に、セクション{target_section}と他のセクションとの間に追加すべき概念リンクを提案してください。

### 検討すべき観点:

1. **同一概念の異なる側面**: 同じ概念が異なる章で異なる文脈で説明されている場合
2. **上位・下位関係**: ある章の概念が他章の概念の具体例や抽象化である場合
3. **因果関係**: ある章の概念が他章の概念の原因や結果となっている場合
4. **対比関係**: 対照的な概念や代替案として提示されている場合
5. **発展関係**: ある章の概念が他章で詳細化・発展している場合

### 出力形式:

以下のJSON形式で、章間リンクを提案してください：

```json
{{
  "cross_chapter_links": [
    {{
      "source_section": "{target_section}",
      "source_concept": "現セクションの概念名",
      "target_section": "他セクションID",
      "target_concept": "他セクションの概念名",
      "relation": "関係の短い説明（1-3語）",
      "relation_description": "関係の詳細説明",
      "confidence": 0.8,
      "reasoning": "このリンクを提案する理由"
    }}
  ]
}}
```

### 注意事項:
- 既に検出された類似概念だけでなく、意味的に関連する概念も積極的に提案してください
- 各リンクには明確な理由付けを含めてください
- confidence は 0.0-1.0 の範囲で、リンクの確実性を示してください
"""
    
    return prompt


def create_batch_prompt_for_all_sections(analysis: Dict) -> str:
    """全セクション間のリンク発見用バッチプロンプトを生成"""
    
    section_nodes = analysis['section_nodes']
    
    # 各セクションの概念サマリーを作成
    section_summaries = []
    for section, nodes in sorted(section_nodes.items()):
        concepts = [f"  - {node['label']}" for node in nodes[:10]]  # 上位10概念
        section_summaries.append(f"セクション {section}:\n" + '\n'.join(concepts))
    
    all_sections_text = '\n\n'.join(section_summaries)
    
    # 既に検出された類似概念
    similar_pairs = analysis['similar_concepts'][:20]  # 上位20ペア
    similar_text = '\n'.join([
        f"- '{node1['label']}' (sec{extract_section_from_node(node1)}) ⟷ "
        f"'{node2['label']}' (sec{extract_section_from_node(node2)}) "
        f"[類似度: {sim:.2f}]"
        for node1, node2, sim in similar_pairs
    ])
    
    prompt = f"""# Plurality概念マップ: 章間リンクの包括的発見

## 全セクションの概念一覧:

{all_sections_text}

## 自動検出された類似概念ペア:

{similar_text}

## タスク:

Pluralityの文書全体を通じて、異なる章（セクション）間で関連する概念のリンクを発見し、提案してください。

### 特に注目すべきパターン:

1. **中核概念の展開**: 「プルラリティ」「デジタル民主主義」「協働テクノロジー」などの中核概念が各章でどのように展開されているか

2. **理論から実践への橋渡し**: 
   - 3章（理論）→ 4章（権利とシステム）→ 5章（技術）→ 6章（応用）の流れ

3. **台湾の事例の参照**:
   - 2-1（玉山）、2-2（日常）の具体例が他章の理論とどう結びつくか

4. **技術概念の相互参照**:
   - 分散型ID、QV、ラディカルマーケットなどの技術が複数章で言及される場合

5. **対立概念の明確化**:
   - 一元論的アトム主義 vs プルラリティ
   - 中央集権 vs 分散型

### 出力形式:

以下のJSON形式で、最も重要な章間リンクを20-30個提案してください：

```json
{{
  "cross_chapter_links": [
    {{
      "source_section": "セクションID",
      "source_concept": "概念名",
      "target_section": "セクションID", 
      "target_concept": "概念名",
      "relation": "関係タイプ",
      "relation_description": "なぜこのリンクが重要か",
      "confidence": 0.9,
      "pattern": "上記パターン1-5のどれに該当するか"
    }}
  ],
  "summary": {{
    "total_links": 数値,
    "key_bridge_concepts": ["章を繋ぐ重要概念のリスト"],
    "network_insights": "発見されたネットワーク構造の洞察"
  }}
}}
```

### 優先順位:
1. 読者の理解を深める教育的価値の高いリンク
2. 分断されたグラフを連結する構造的に重要なリンク
3. Pluralityの核心的議論を明確にするリンク
"""
    
    return prompt


def main():
    # 結合グラフを読み込み
    merged_graph_path = Path('webui/public/graph_merged.json')
    
    if not merged_graph_path.exists():
        print(f"Error: {merged_graph_path} not found. Run merge_graphs.py first.")
        return
    
    graph = load_merged_graph(merged_graph_path)
    print(f"Loaded merged graph with {len(graph['nodes'])} nodes")
    
    # 関係性を分析
    analysis = analyze_concept_relationships(graph)
    
    # 統計情報を表示
    print(f"\nAnalysis Results:")
    print(f"- Sections found: {len(analysis['section_nodes'])}")
    print(f"- Similar concept pairs: {len(analysis['similar_concepts'])}")
    
    # 類似概念の上位を表示
    print("\nTop Similar Concepts Across Chapters:")
    for node1, node2, similarity in analysis['similar_concepts'][:10]:
        print(f"  {node1['label']} (sec{extract_section_from_node(node1)}) ⟷ "
              f"{node2['label']} (sec{extract_section_from_node(node2)}) "
              f"[{similarity:.2f}]")
    
    # バッチプロンプトを生成
    batch_prompt = create_batch_prompt_for_all_sections(analysis)
    
    # プロンプトを保存
    output_path = Path('cross_chapter_links_prompt.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(batch_prompt)
    
    print(f"\nBatch prompt saved to: {output_path}")
    
    # 個別セクション用プロンプトの例も生成
    example_section = '3-0'  # 例として3-0を使用
    if example_section in analysis['section_nodes']:
        individual_prompt = create_link_discovery_prompt(analysis, example_section)
        example_output_path = Path(f'cross_chapter_links_prompt_{example_section}.txt')
        with open(example_output_path, 'w', encoding='utf-8') as f:
            f.write(individual_prompt)
        print(f"Example individual prompt for section {example_section} saved to: {example_output_path}")


if __name__ == '__main__':
    main()