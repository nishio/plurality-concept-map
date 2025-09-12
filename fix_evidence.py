#!/usr/bin/env python3
"""
証拠テキストの不正確な引用を原文に基づいて自動修正するスクリプト
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher


def load_graph_data(graph_file: Path) -> Dict:
    """グラフデータを読み込み"""
    with open(graph_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_graph_data(graph_file: Path, data: Dict):
    """グラフデータを保存"""
    with open(graph_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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


def find_best_match_in_source(evidence_text: str, source_text: str) -> Optional[str]:
    """
    ソーステキスト内で証拠テキストに最も近い部分を検索し、正確な原文を返す
    """
    evidence_normalized = normalize_text(evidence_text)
    source_normalized = normalize_text(source_text)
    
    # まず完全一致を試行
    if evidence_normalized in source_normalized:
        return evidence_text  # 既に正確
    
    # 部分一致を検索
    evidence_words = evidence_normalized.split()
    if len(evidence_words) < 3:
        return None  # 短すぎる場合はスキップ
    
    best_match = None
    best_similarity = 0.7  # 最低70%の類似度を要求
    
    # 前後に余裕を持たせた検索範囲
    for window_factor in [1.0, 1.2, 0.8]:  # 同じ長さ、20%長い、20%短い
        window_size = int(len(evidence_normalized) * window_factor)
        
        for i in range(len(source_normalized) - window_size + 1):
            window_text = source_normalized[i:i + window_size]
            similarity = SequenceMatcher(None, evidence_normalized, window_text).ratio()
            
            if similarity > best_similarity:
                best_similarity = similarity
                # 正規化前のテキストから対応する部分を抽出
                # 簡単な方法：source_textで同様の位置を探す
                best_match = extract_original_text(source_text, window_text, evidence_text)
    
    return best_match


def extract_original_text(source_text: str, normalized_match: str, original_evidence: str) -> str:
    """
    正規化されたマッチテキストから元のソーステキストでの対応部分を抽出
    """
    # 正規化されたマッチテキストの最初と最後の数語を使ってオリジナルテキストを検索
    match_words = normalized_match.split()
    if len(match_words) < 3:
        return normalized_match
    
    # 最初の3語と最後の3語でパターンを作成
    start_pattern = ' '.join(match_words[:3])
    end_pattern = ' '.join(match_words[-3:])
    
    # ソーステキストから対応部分を検索
    source_normalized = normalize_text(source_text)
    start_pos = source_normalized.find(start_pattern)
    end_pos = source_normalized.rfind(end_pattern)
    
    if start_pos != -1 and end_pos != -1 and start_pos <= end_pos:
        # 正規化されていないソーステキストから対応部分を大まかに抽出
        # より正確な実装が必要だが、とりあえず正規化されたテキストを返す
        extracted = source_normalized[start_pos:end_pos + len(end_pattern)]
        return extracted.strip()
    
    return normalized_match


def fix_evidence_in_graph(graph_file: Path, source_dir: Path) -> int:
    """グラフファイル内の証拠テキストを修正"""
    graph_data = load_graph_data(graph_file)
    
    # ソースファイルを特定
    if 'extra-1' in str(graph_file):
        source_file = source_dir / '1.md'
    elif 'extra-2' in str(graph_file):
        source_file = source_dir / '2.md'
    elif 'extra-3' in str(graph_file):
        source_file = source_dir / '3.md'
    else:
        print(f"Unknown graph file pattern: {graph_file}")
        return 0
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        return 0
    
    source_text = load_source_text(source_file)
    fixes_made = 0
    
    # 特別な修正マッピング（手動で確認した正確な引用）
    manual_fixes = {
        # extra-1の修正
        "私たちこそが未来の共同設計者である。": "私たちこそが未来の共同設計者である",
        "新たな対話を始めて溝を埋め、周縁化されがちな声を増幅するプラットフォームを設計したり。": "新たな対話を始めて溝を埋め、周縁化されがちな声を増幅するプラットフォームを設計したり",
        "プルラリティは「社会的差異を超えたコラボレーションのための技術」と定義されています。": "「社会的差異を超えたコラボレーションのための技術」と定義されています",
        "中央集権的なプラットフォームが、私たちのつながりから価値を搾取する一方で、社会的な結びつきを根こそぎ奪う恐れがある。": "中央集権的なプラットフォームが、私たちのつながりから価値を搾取する一方で、共有しているという現実感を損なわせ、社会的な結びつきを根こそぎ奪う恐れがある",
        
        # extra-2の修正  
        "これほどの文化的差異や、この対話に到るまでのまったく異なる道筋を超えて私たちの視点が共振した。": "これほどの文化的差異や、この対話に到るまでのまったく異なる道筋を超えて私たちの視点が共振したことで、会の終わり頃になると私は目頭が熱くなったほどだった",
        "プルラリティは、台湾のデジタル民主主義を牽引する初代デジタル大臣オードリー・タンとマイクロソフト首席研究員にして気鋭の経済学者E・グレン・ワイルが提唱する新たな社会ビジョンです。": "プルラリティ（多元性）は、台湾のデジタル民主主義を牽引する初代デジタル大臣オードリー・タンとマイクロソフト首席研究員にして気鋭の経済学者E・グレン・ワイルが提唱する新たな社会ビジョンです",
        "文化的差異や、この対話に到るまでのまったく異なる道筋を超えて私たちの視点が共振した。": "文化的差異や、この対話に到るまでのまったく異なる道筋を超えて私たちの視点が共振したことで、会の終わり頃になると私は目頭が熱くなったほどだった",
        "イノベーションの伝統の、待ちに待った、そして必然的なリバイバルとして見られている。": "イノベーションの伝統の、待ちに待った、そして必然的なリバイバルとして見られている",
        "社会的差異を超えたコラボレーションのための技術と定義されています。": "「社会的差異を超えたコラボレーションのための技術」と定義されています",
        
        # extra-3の修正
        "『コオペレーション』にはこの意味合いも含まれるが、必ずしも創造的な相乗効果を伴わず、より取引的な相互作用を指す場合もある。": "『コオペレーション』にはこの意味合いも含まれるが、必ずしも創造的な相乗効果を伴わず、より取引的な相互作用を指す場合もある",
        "QVでは、各参加者に与えられた「投票権（ボイスクレジット）」を自由に配分して複数票を投じることができる。": "QVでは、各参加者に与えられた「投票権（ボイスクレジット）」を自由に配分して複数票を投じることができる",
        "AIが大規模なコメントの分類や要約作業を代行したらどうなるか。": "AIが大規模なコメントの分類や要約作業を代行したらどうなるか",
        
        # ⿻記号の問題
        "この博物館が私の想像よりもはるかに⿻の精神をホーリスティックに体現していることがわかってきた。": "この博物館が私の想像よりもはるかにプルラリティの精神をホーリスティックに体現していることがわかってきた",
        "この博物館が私の想像よりもはるかにプルラリティの精神をホーリスティックに体現していることがわかってきた。": "この博物館が私の想像よりもはるかにプルラリティの精神をホーリスティックに体現していることがわかってきた"
    }
    
    # ノードの証拠を修正
    for node in graph_data.get('nodes', []):
        evidences = node.get('evidence', [])
        for i, evidence_item in enumerate(evidences):
            if isinstance(evidence_item, dict):
                evidence_text = evidence_item.get('text', '')
                if evidence_text in manual_fixes:
                    evidence_item['text'] = manual_fixes[evidence_text]
                    fixes_made += 1
                    print(f"✅ Fixed node {node.get('id', 'unknown')} evidence {i+1}")
    
    # エッジの証拠を修正
    for edge in graph_data.get('edges', []):
        evidences = edge.get('evidence', [])
        for i, evidence_item in enumerate(evidences):
            if isinstance(evidence_item, dict):
                evidence_text = evidence_item.get('text', '')
                if evidence_text in manual_fixes:
                    evidence_item['text'] = manual_fixes[evidence_text]
                    fixes_made += 1
                    print(f"✅ Fixed edge {edge.get('source', 'unknown')} -> {edge.get('target', 'unknown')} evidence {i+1}")
    
    # 修正されたデータを保存
    if fixes_made > 0:
        save_graph_data(graph_file, graph_data)
        print(f"💾 Saved {fixes_made} fixes to {graph_file.name}")
    
    return fixes_made


def main():
    graph_dir = Path('webui/public')
    source_dir = Path('extra-input')
    
    graph_files = [
        graph_dir / 'graph_extra-1.json',
        graph_dir / 'graph_extra-2.json',
        graph_dir / 'graph_extra-3.json'
    ]
    
    total_fixes = 0
    
    for graph_file in graph_files:
        if not graph_file.exists():
            print(f"⚠️  Graph file not found: {graph_file}")
            continue
            
        print(f"🔧 Fixing {graph_file.name}...")
        fixes = fix_evidence_in_graph(graph_file, source_dir)
        total_fixes += fixes
    
    print(f"\n✨ Total fixes applied: {total_fixes}")
    print("🔍 Run 'python validate_evidence.py' to verify the fixes")
    
    return 0


if __name__ == '__main__':
    exit(main())