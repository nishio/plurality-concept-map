#!/usr/bin/env python3
"""
グラフファイルを結合し、ID衝突を回避するスクリプト
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict


def load_graph(filepath: Path) -> Dict[str, Any]:
    """グラフファイルを読み込む"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_section_id(filename: str) -> str:
    """ファイル名からセクションIDを抽出"""
    # graph_sec0-2.json -> 0-2
    if filename.startswith('graph_sec'):
        return filename.replace('graph_sec', '').replace('.json', '')
    return ''


def check_id_collision(graphs: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """ID衝突をチェックして返す"""
    id_to_sections = defaultdict(list)
    
    for section_id, graph in graphs.items():
        for node in graph.get('nodes', []):
            node_id = node.get('id')
            if node_id:
                id_to_sections[node_id].append(section_id)
    
    # 衝突しているIDのみを返す
    collisions = {id_: sections for id_, sections in id_to_sections.items() if len(sections) > 1}
    return collisions


def create_unique_id(original_id: str, section_id: str) -> str:
    """衝突回避のためのユニークIDを作成"""
    return f"{original_id}_sec{section_id}"


def merge_graphs(graph_files: List[Path]) -> Dict[str, Any]:
    """グラフファイルを結合"""
    merged = {
        'nodes': [],
        'edges': [],
        'metadata': {
            'merged_from': [],
            'total_sections': 0
        }
    }
    
    # 各グラフを読み込み
    graphs = {}
    for filepath in graph_files:
        section_id = extract_section_id(filepath.name)
        if section_id:
            graphs[section_id] = load_graph(filepath)
            merged['metadata']['merged_from'].append({
                'section_id': section_id,
                'file': filepath.name
            })
    
    merged['metadata']['total_sections'] = len(graphs)
    
    # ID衝突をチェック
    collisions = check_id_collision(graphs)
    print(f"Found {len(collisions)} ID collisions")
    
    if collisions:
        print("\nColliding IDs:")
        for id_, sections in collisions.items():
            print(f"  '{id_}' appears in sections: {', '.join(sections)}")
    
    # IDマッピングを作成（古いID -> 新しいID）
    id_mapping = {}
    
    for section_id, graph in graphs.items():
        section_mapping = {}
        
        # ノードのIDマッピングを作成
        for node in graph.get('nodes', []):
            original_id = node.get('id')
            if original_id:
                if original_id in collisions:
                    # 衝突がある場合は新しいIDを作成
                    new_id = create_unique_id(original_id, section_id)
                    section_mapping[original_id] = new_id
                else:
                    # 衝突がない場合はそのまま使用
                    section_mapping[original_id] = original_id
        
        id_mapping[section_id] = section_mapping
    
    # ノードを結合
    all_node_ids = set()
    for section_id, graph in graphs.items():
        section_mapping = id_mapping[section_id]
        
        for node in graph.get('nodes', []):
            original_id = node.get('id')
            if original_id:
                new_id = section_mapping[original_id]
                
                # IDを更新
                node_copy = node.copy()
                node_copy['id'] = new_id
                node_copy['original_id'] = original_id  # 元のIDを保持
                node_copy['source_section'] = section_id  # ソースセクションを記録
                
                # 重複チェック（念のため）
                if new_id not in all_node_ids:
                    merged['nodes'].append(node_copy)
                    all_node_ids.add(new_id)
    
    # エッジを結合
    all_edges = set()
    for section_id, graph in graphs.items():
        section_mapping = id_mapping[section_id]
        
        for edge in graph.get('edges', []):
            source = edge.get('source')
            target = edge.get('target')
            
            if source and target:
                # ソースとターゲットのIDを更新
                new_source = section_mapping.get(source, source)
                new_target = section_mapping.get(target, target)
                
                edge_copy = edge.copy()
                edge_copy['source'] = new_source
                edge_copy['target'] = new_target
                edge_copy['original_source'] = source  # 元のIDを保持
                edge_copy['original_target'] = target  # 元のIDを保持
                edge_copy['source_section'] = section_id  # ソースセクションを記録
                
                # エッジの重複チェック
                edge_key = (new_source, new_target, edge.get('relation', ''))
                if edge_key not in all_edges:
                    merged['edges'].append(edge_copy)
                    all_edges.add(edge_key)
    
    # 統計情報を追加
    merged['metadata']['statistics'] = {
        'total_nodes': len(merged['nodes']),
        'total_edges': len(merged['edges']),
        'id_collisions_resolved': len(collisions),
        'unique_node_ids': len(all_node_ids)
    }
    
    return merged


def validate_merged_graph(graph: Dict[str, Any]) -> List[str]:
    """結合されたグラフの妥当性をチェック"""
    issues = []
    
    # ノードIDの重複チェック
    node_ids = [node['id'] for node in graph['nodes']]
    if len(node_ids) != len(set(node_ids)):
        issues.append("Duplicate node IDs found in merged graph")
    
    # エッジの参照整合性チェック
    node_id_set = set(node_ids)
    for edge in graph['edges']:
        if edge['source'] not in node_id_set:
            issues.append(f"Edge references non-existent source: {edge['source']}")
        if edge['target'] not in node_id_set:
            issues.append(f"Edge references non-existent target: {edge['target']}")
    
    return issues


def main():
    # グラフファイルのディレクトリ
    graph_dir = Path('webui/public')
    
    # すべてのグラフファイルを取得
    graph_files = sorted(graph_dir.glob('graph_sec*.json'))
    print(f"Found {len(graph_files)} graph files to merge")
    
    if not graph_files:
        print("No graph files found!")
        return
    
    # グラフを結合
    merged_graph = merge_graphs(graph_files)
    
    # 検証
    issues = validate_merged_graph(merged_graph)
    if issues:
        print("\nValidation issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nValidation passed: No issues found")
    
    # 結果を保存
    output_path = graph_dir / 'graph_merged.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_graph, f, ensure_ascii=False, indent=2)
    
    print(f"\nMerged graph saved to: {output_path}")
    print(f"  Total nodes: {merged_graph['metadata']['statistics']['total_nodes']}")
    print(f"  Total edges: {merged_graph['metadata']['statistics']['total_edges']}")
    print(f"  ID collisions resolved: {merged_graph['metadata']['statistics']['id_collisions_resolved']}")


if __name__ == '__main__':
    main()