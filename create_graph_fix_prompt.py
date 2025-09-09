#!/usr/bin/env python3
"""
グラフデータ修正用プロンプト作成ツール
連結でないグラフデータを修正するために必要な情報を収集してプロンプトを生成
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
import sys

def load_markdown_file(filepath: Path) -> str:
    """Markdownファイルを読み込む"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        sys.exit(1)

def load_graph_data(graph_dir: Path, section_id: str) -> Dict[str, Any]:
    """指定されたセクションのグラフデータを読み込む"""
    graph_file = graph_dir / f"graph_{section_id}.json"
    
    try:
        with open(graph_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Graph file not found: {graph_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {graph_file}: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading graph file: {e}")
        sys.exit(1)

def get_extraction_prompts() -> Dict[str, str]:
    """概念と関係抽出に使用したプロンプトを取得"""
    prompts = {}
    
    # プロンプトテンプレートを直接埋め込み（prompts.pyから）
    prompts['concept_extraction'] = """You are given a section from a textbook chapter.

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
- Evidence must be *verbatim* spans inside the section."""
    
    prompts['relation_extraction'] = """You are given a list of concept labels and the same section text.
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
- Use the original language of the text: if the source text is in Japanese, use Japanese for both relation and relation_description.
- Evidence must ground the relation; omit the edge if no textual support.
- Keep 3-12 edges per section."""
    
    return prompts

def analyze_graph_connectivity(graph_data: Dict[str, Any]) -> Dict[str, Any]:
    """グラフの連結性を分析"""
    nodes = graph_data.get('nodes', [])
    edges = graph_data.get('edges', [])
    
    # ノードIDのセットを作成
    node_ids = {node['id'] for node in nodes}
    
    # 各ノードの接続を追跡
    connections = {node_id: set() for node_id in node_ids}
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        if source in node_ids and target in node_ids:
            connections[source].add(target)
            connections[target].add(source)
    
    # 連結成分を見つける
    visited = set()
    components = []
    
    def dfs(node, component):
        visited.add(node)
        component.add(node)
        for neighbor in connections[node]:
            if neighbor not in visited:
                dfs(neighbor, component)
    
    for node_id in node_ids:
        if node_id not in visited:
            component = set()
            dfs(node_id, component)
            components.append(component)
    
    # 孤立ノードを特定
    isolated_nodes = [node_id for node_id in node_ids if len(connections[node_id]) == 0]
    
    return {
        'total_nodes': len(nodes),
        'total_edges': len(edges),
        'num_components': len(components),
        'components': [list(comp) for comp in components],
        'isolated_nodes': isolated_nodes,
        'is_connected': len(components) == 1
    }

def create_fix_prompt(markdown_content: str, graph_data: Dict[str, Any], 
                     section_id: str, max_concepts: int = 15) -> str:
    """グラフ修正用のプロンプトを生成"""
    
    prompts = get_extraction_prompts()
    connectivity = analyze_graph_connectivity(graph_data)
    
    prompt = f"""# グラフデータ修正タスク

以下のセクションから抽出された概念グラフが連結でない状態になっています。
グラフを連結にするために、既存の概念間に新たな関係（エッジ）を追加するか、
必要に応じて概念の統合・修正を提案してください。

## 現在のグラフ分析
- 総ノード数: {connectivity['total_nodes']}
- 総エッジ数: {connectivity['total_edges']}
- 連結成分数: {connectivity['num_components']}
- 孤立ノード: {', '.join(connectivity['isolated_nodes']) if connectivity['isolated_nodes'] else 'なし'}

## 元のMarkdownセクション (Section ID: {section_id})
```markdown
{markdown_content}
```

## 概念抽出に使用したプロンプト
```
{prompts['concept_extraction']}
```

## 関係抽出に使用したプロンプト
```
{prompts['relation_extraction']}
```

## 現在の抽出済みデータ

### 概念（ノード）
```json
{json.dumps(graph_data['nodes'], ensure_ascii=False, indent=2)}
```

### 関係（エッジ）
```json
{json.dumps(graph_data['edges'], ensure_ascii=False, indent=2)}
```

## 修正指示

1. 上記のグラフが連結になるように、以下の修正を提案してください：
   - 孤立したノード間に適切な関係を追加
   - 連結成分間を繋ぐ関係を追加
   - 必要に応じて、重複する概念の統合を提案

2. 修正案は以下の形式で提供してください：

### 追加すべきエッジ
```json
{{
  "new_edges": [
    {{
      "source_label": "概念A",
      "target_label": "概念B",
      "relation": "関係ラベル",
      "relation_description": "完全な関係の説明",
      "confidence": 0.8,
      "evidence": [{{"text": "テキストからの証拠"}}]
    }}
  ]
}}
```

### 統合すべき概念（もしあれば）
```json
{{
  "merge_concepts": [
    {{
      "concepts_to_merge": ["概念1", "概念2"],
      "merged_label": "統合後のラベル",
      "reason": "統合の理由"
    }}
  ]
}}
```

注意事項：
- 元のテキストに基づいた自然な関係のみを追加してください
- エビデンスは必ず元のテキストから引用してください
- 日本語のテキストの場合は日本語でラベルと説明を記述してください
"""
    
    return prompt

def save_prompt(prompt: str, output_path: Path):
    """プロンプトをファイルに保存"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"Prompt saved to: {output_path}")
    except Exception as e:
        print(f"Error saving prompt: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='グラフデータ修正用のプロンプトを作成'
    )
    parser.add_argument(
        '--markdown',
        required=True,
        type=Path,
        help='対象セクションのMarkdownファイルパス'
    )
    parser.add_argument(
        '--graph-dir',
        required=True,
        type=Path,
        help='グラフデータが保存されているディレクトリ'
    )
    parser.add_argument(
        '--section-id',
        required=True,
        help='セクションID（例: 0-1, 1-2など）'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('graph_fix_prompt.txt'),
        help='プロンプトの出力先ファイル（デフォルト: graph_fix_prompt.txt）'
    )
    parser.add_argument(
        '--max-concepts',
        type=int,
        default=15,
        help='最大概念数（デフォルト: 15）'
    )
    
    args = parser.parse_args()
    
    # データを読み込み
    print(f"Loading markdown from: {args.markdown}")
    markdown_content = load_markdown_file(args.markdown)
    
    print(f"Loading graph data from: {args.graph_dir}/graph_{args.section_id}.json")
    graph_data = load_graph_data(args.graph_dir, args.section_id)
    
    # グラフの連結性を分析
    connectivity = analyze_graph_connectivity(graph_data)
    print(f"\nGraph connectivity analysis:")
    print(f"  - Connected: {connectivity['is_connected']}")
    print(f"  - Components: {connectivity['num_components']}")
    print(f"  - Isolated nodes: {len(connectivity['isolated_nodes'])}")
    
    # プロンプトを生成
    print("\nGenerating fix prompt...")
    prompt = create_fix_prompt(
        markdown_content,
        graph_data,
        args.section_id,
        args.max_concepts
    )
    
    # プロンプトを保存
    save_prompt(prompt, args.output)
    
    # プロンプトをコンソールにも表示（オプション）
    print("\n" + "="*50)
    print("Generated prompt preview (first 1000 chars):")
    print("="*50)
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)

if __name__ == "__main__":
    main()