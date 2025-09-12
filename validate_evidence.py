#!/usr/bin/env python3
"""
証拠テキストと原文の整合性を検証するスクリプト
Text fragment linkが失敗する原因となる不正確な引用を検出
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
from difflib import SequenceMatcher


def load_graph_data(graph_file: Path) -> Dict:
    """グラフデータを読み込み"""
    with open(graph_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_source_text(source_file: Path) -> str:
    """ソーステキストを読み込み"""
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Markdownファイルの場合、冒頭のメタデータを除去
        lines = content.split('\n')
        # URLやタイトル行をスキップして本文を取得
        content_start = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('http') and '|' not in line and not line.startswith('#'):
                # 本文の開始を検出
                content_start = i
                break
        return '\n'.join(lines[content_start:])


def normalize_text(text: str) -> str:
    """テキストを正規化（空白、改行、句読点の統一）"""
    # 改行を空白に変換
    text = re.sub(r'\s+', ' ', text)
    # 句読点前後の空白を調整
    text = re.sub(r'\s*([。、！？])\s*', r'\1', text)
    # 全角・半角の統一
    text = text.replace('　', ' ')  # 全角空白を半角に
    return text.strip()


def find_text_in_source(evidence_text: str, source_text: str, threshold: float = 0.8) -> Optional[Tuple[str, float, int, int]]:
    """
    ソーステキスト内で証拠テキストに最も近い部分を検索
    
    Returns:
        (matched_text, similarity, start_pos, end_pos) または None
    """
    evidence_normalized = normalize_text(evidence_text)
    source_normalized = normalize_text(source_text)
    
    # まず完全一致を試行
    if evidence_normalized in source_normalized:
        start_pos = source_normalized.find(evidence_normalized)
        end_pos = start_pos + len(evidence_normalized)
        return evidence_normalized, 1.0, start_pos, end_pos
    
    # 部分一致を検索（スライディングウィンドウ）
    evidence_length = len(evidence_normalized)
    best_match = None
    best_similarity = 0.0
    
    # 前後に余裕を持たせた検索範囲
    search_ranges = [
        evidence_length,  # 同じ長さ
        int(evidence_length * 1.2),  # 20%長い
        int(evidence_length * 0.8),   # 20%短い
    ]
    
    for window_size in search_ranges:
        for i in range(len(source_normalized) - window_size + 1):
            window_text = source_normalized[i:i + window_size]
            similarity = SequenceMatcher(None, evidence_normalized, window_text).ratio()
            
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = (window_text, similarity, i, i + window_size)
    
    return best_match


def validate_evidence_in_graph(graph_file: Path, source_dir: Path) -> List[Dict]:
    """グラフファイル内の全証拠テキストを検証"""
    graph_data = load_graph_data(graph_file)
    issues = []
    
    # ソースファイルを特定
    if 'extra-1' in str(graph_file):
        source_file = source_dir / '1.md'
    elif 'extra-2' in str(graph_file):
        source_file = source_dir / '2.md'
    elif 'extra-3' in str(graph_file):
        source_file = source_dir / '3.md'
    else:
        print(f"Unknown graph file pattern: {graph_file}")
        return issues
    
    if not source_file.exists():
        issues.append({
            'type': 'missing_source',
            'message': f"Source file not found: {source_file}",
            'graph_file': str(graph_file)
        })
        return issues
    
    source_text = load_source_text(source_file)
    
    # ノードの証拠を検証
    for node in graph_data.get('nodes', []):
        node_id = node.get('id', 'unknown')
        evidences = node.get('evidence', [])
        
        for i, evidence_item in enumerate(evidences):
            # evidenceが辞書形式の場合はtextフィールドを取得
            if isinstance(evidence_item, dict):
                evidence_text = evidence_item.get('text', '')
            else:
                evidence_text = str(evidence_item)
                
            if not evidence_text.strip():
                continue
                
            match_result = find_text_in_source(evidence_text, source_text)
            
            if match_result is None:
                issues.append({
                    'type': 'evidence_not_found',
                    'node_id': node_id,
                    'evidence_index': i,
                    'evidence_text': evidence_text[:100] + ('...' if len(evidence_text) > 100 else ''),
                    'graph_file': str(graph_file),
                    'source_file': str(source_file)
                })
            elif match_result[1] < 1.0:  # 完全一致でない場合
                matched_text, similarity, start_pos, end_pos = match_result
                issues.append({
                    'type': 'evidence_mismatch',
                    'node_id': node_id,
                    'evidence_index': i,
                    'evidence_text': evidence_text,
                    'matched_text': matched_text,
                    'similarity': similarity,
                    'graph_file': str(graph_file),
                    'source_file': str(source_file)
                })
    
    # エッジの証拠を検証
    for edge in graph_data.get('edges', []):
        source_id = edge.get('source', 'unknown')
        target_id = edge.get('target', 'unknown')
        evidences = edge.get('evidence', [])
        
        for i, evidence_item in enumerate(evidences):
            # evidenceが辞書形式の場合はtextフィールドを取得
            if isinstance(evidence_item, dict):
                evidence_text = evidence_item.get('text', '')
            else:
                evidence_text = str(evidence_item)
                
            if not evidence_text.strip():
                continue
                
            match_result = find_text_in_source(evidence_text, source_text)
            
            if match_result is None:
                issues.append({
                    'type': 'evidence_not_found',
                    'edge': f"{source_id} -> {target_id}",
                    'evidence_index': i,
                    'evidence_text': evidence_text[:100] + ('...' if len(evidence_text) > 100 else ''),
                    'graph_file': str(graph_file),
                    'source_file': str(source_file)
                })
            elif match_result[1] < 1.0:  # 完全一致でない場合
                matched_text, similarity, start_pos, end_pos = match_result
                issues.append({
                    'type': 'evidence_mismatch',
                    'edge': f"{source_id} -> {target_id}",
                    'evidence_index': i,
                    'evidence_text': evidence_text,
                    'matched_text': matched_text,
                    'similarity': similarity,
                    'graph_file': str(graph_file),
                    'source_file': str(source_file)
                })
    
    return issues


def print_validation_report(issues: List[Dict]):
    """検証結果をレポート形式で出力"""
    if not issues:
        print("✅ All evidence texts match their source files perfectly!")
        return
    
    print(f"⚠️  Found {len(issues)} evidence validation issues:\n")
    
    # 問題タイプ別に整理
    by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in by_type:
            by_type[issue_type] = []
        by_type[issue_type].append(issue)
    
    for issue_type, type_issues in by_type.items():
        print(f"## {issue_type.upper().replace('_', ' ')} ({len(type_issues)} issues)")
        
        for issue in type_issues:
            graph_file = Path(issue['graph_file']).name
            
            if 'node_id' in issue:
                print(f"📍 Node: {issue['node_id']} (in {graph_file})")
            elif 'edge' in issue:
                print(f"📍 Edge: {issue['edge']} (in {graph_file})")
            
            if issue_type == 'evidence_mismatch':
                print(f"   Similarity: {issue['similarity']:.2f}")
                print(f"   📝 Evidence: {issue['evidence_text'][:150]}...")
                print(f"   📄 Source:   {issue['matched_text'][:150]}...")
            elif issue_type == 'evidence_not_found':
                print(f"   📝 Evidence: {issue['evidence_text']}")
            
            print(f"   📂 Source: {Path(issue['source_file']).name}")
            print()
        
        print()


def main():
    parser = argparse.ArgumentParser(description='Validate evidence texts against source files')
    parser.add_argument('--graph-dir', type=str, default='webui/public', 
                       help='Directory containing graph JSON files')
    parser.add_argument('--source-dir', type=str, default='extra-input',
                       help='Directory containing source markdown files')
    parser.add_argument('--threshold', type=float, default=0.8,
                       help='Similarity threshold for matches (0.0-1.0)')
    
    args = parser.parse_args()
    
    graph_dir = Path(args.graph_dir)
    source_dir = Path(args.source_dir)
    
    if not graph_dir.exists():
        print(f"❌ Graph directory not found: {graph_dir}")
        return 1
    
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1
    
    # extraファイルのみを対象に検証
    graph_files = [
        graph_dir / 'graph_extra-1.json',
        graph_dir / 'graph_extra-2.json', 
        graph_dir / 'graph_extra-3.json'
    ]
    
    all_issues = []
    
    for graph_file in graph_files:
        if not graph_file.exists():
            print(f"⚠️  Graph file not found: {graph_file}")
            continue
            
        print(f"🔍 Validating {graph_file.name}...")
        issues = validate_evidence_in_graph(graph_file, source_dir)
        all_issues.extend(issues)
    
    print(f"\n{'='*60}")
    print("VALIDATION REPORT")
    print('='*60)
    print_validation_report(all_issues)
    
    return 0 if not all_issues else 1


if __name__ == '__main__':
    exit(main())