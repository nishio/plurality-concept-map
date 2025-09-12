#!/usr/bin/env python3
"""
残りの4件の証拠問題を修正
"""

import json
from pathlib import Path

def fix_remaining_issues():
    # extra-2の修正
    extra2_file = Path('webui/public/graph_extra-2.json')
    with open(extra2_file, 'r', encoding='utf-8') as f:
        data2 = json.load(f)
    
    fixes_made = 0
    
    # 1. プルラリティ -> デジタル民主主義 のエッジを修正
    for edge in data2.get('edges', []):
        if edge.get('source') == 'プルラリティ' and edge.get('target') == 'デジタル民主主義':
            for evidence_item in edge.get('evidence', []):
                if isinstance(evidence_item, dict):
                    old_text = evidence_item.get('text', '')
                    if old_text.startswith('プルラリティ（多元性）は、台湾の'):
                        evidence_item['text'] = 'PLURALITY（プルラリティ）は、台湾のデジタル民主主義を牽引する初代デジタル大臣オードリー・タンとマイクロソフト首席研究員にして気鋭の経済学者E・グレン・ワイルが提唱する新たな社会ビジョンです'
                        fixes_made += 1
                        print("✅ Fixed プルラリティ -> デジタル民主主義 edge")
    
    # 2. ホーリスティック関連の証拠を修正（⿻記号を使った正確な引用に修正）
    for node in data2.get('nodes', []):
        if node.get('id') == 'ホーリスティック':
            for evidence_item in node.get('evidence', []):
                if isinstance(evidence_item, dict):
                    evidence_item['text'] = 'この博物館が私の想像よりもはるかに⿻（訳注：本書では「プルラリティ」をユニコードの⿻を使って表現する場合がある。）の精神をホーリスティックに体現していることがわかってきた'
                    fixes_made += 1
                    print("✅ Fixed ホーリスティック node")
    
    for edge in data2.get('edges', []):
        if edge.get('source') == 'ホーリスティック' and edge.get('target') == 'プルラリティ':
            for evidence_item in edge.get('evidence', []):
                if isinstance(evidence_item, dict):
                    evidence_item['text'] = 'この博物館が私の想像よりもはるかに⿻（訳注：本書では「プルラリティ」をユニコードの⿻を使って表現する場合がある。）の精神をホーリスティックに体現していることがわかってきた'
                    fixes_made += 1
                    print("✅ Fixed ホーリスティック -> プルラリティ edge")
    
    # extra-2のデータを保存
    if fixes_made > 0:
        with open(extra2_file, 'w', encoding='utf-8') as f:
            json.dump(data2, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved {fixes_made} fixes to graph_extra-2.json")
    
    # extra-3の修正
    extra3_file = Path('webui/public/graph_extra-3.json')
    with open(extra3_file, 'r', encoding='utf-8') as f:
        data3 = json.load(f)
    
    # cooperation ノードの修正
    for node in data3.get('nodes', []):
        if node.get('id') == 'cooperation':
            for evidence_item in node.get('evidence', []):
                if isinstance(evidence_item, dict):
                    old_text = evidence_item.get('text', '')
                    if '『コオペレーション』' in old_text:
                        evidence_item['text'] = '『コオペレーション』にはこの意味合いも含まれるが、必ずしも創造的な相乗効果を伴わず、より取引的な相互作用を指す場合もある'
                        fixes_made += 1
                        print("✅ Fixed cooperation node")
    
    # extra-3のデータを保存
    with open(extra3_file, 'w', encoding='utf-8') as f:
        json.dump(data3, f, ensure_ascii=False, indent=2)
    
    print(f"✨ Total additional fixes: {fixes_made}")
    return fixes_made

if __name__ == '__main__':
    fix_remaining_issues()