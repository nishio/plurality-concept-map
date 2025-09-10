import { Concept, Edge } from '../types';

export interface CrossChapterLink {
  source_section: string;
  source_concept: string;
  target_section: string;
  target_concept: string;
  relation: string;
  relation_description: string;
  confidence: number;
  pattern?: number;
}

export interface CrossChapterLinksData {
  cross_chapter_links: CrossChapterLink[];
  summary: {
    total_links: number;
    key_bridge_concepts: string[];
    network_insights: string;
  };
}

let crossChapterLinksCache: CrossChapterLinksData | null = null;

/**
 * 章間リンクデータを読み込む
 */
export const loadCrossChapterLinks = async (): Promise<CrossChapterLinksData> => {
  if (crossChapterLinksCache) {
    return crossChapterLinksCache;
  }

  try {
    const response = await fetch('./cross_chapter_links.json');
    if (response.ok) {
      const data = await response.json();
      crossChapterLinksCache = data;
      return data;
    }
  } catch (error) {
    console.warn('Failed to load cross-chapter links:', error);
  }

  // フォールバックデータ
  return {
    cross_chapter_links: [],
    summary: {
      total_links: 0,
      key_bridge_concepts: [],
      network_insights: ''
    }
  };
};

/**
 * 指定セクションから外向きの章間リンクを取得
 */
export const getOutgoingLinks = (
  links: CrossChapterLink[], 
  sectionId: string
): CrossChapterLink[] => {
  return links.filter(link => link.source_section === sectionId);
};

/**
 * 指定セクションへの内向きの章間リンクを取得
 */
export const getIncomingLinks = (
  links: CrossChapterLink[], 
  sectionId: string
): CrossChapterLink[] => {
  return links.filter(link => link.target_section === sectionId);
};

/**
 * 特定の概念に関連する章間リンクを取得
 */
export const getConceptCrossChapterLinks = (
  links: CrossChapterLink[], 
  conceptLabel: string
): { outgoing: CrossChapterLink[], incoming: CrossChapterLink[] } => {
  const outgoing = links.filter(link => link.source_concept === conceptLabel);
  const incoming = links.filter(link => link.target_concept === conceptLabel);
  
  return { outgoing, incoming };
};

/**
 * 章間リンクから仮想ノードとエッジを生成
 * 各セクションのグラフに他章の概念を「外部参照ノード」として追加
 */
export const createCrossChapterNodes = (
  links: CrossChapterLink[],
  currentSection: string,
  existingNodes: Concept[]
): { virtualNodes: Concept[], crossEdges: Edge[] } => {
  console.log(`createCrossChapterNodes called for section: ${currentSection}`, {
    totalLinks: links.length,
    existingNodes: existingNodes.length
  });

  const virtualNodes: Concept[] = [];
  const crossEdges: Edge[] = [];
  const existingNodeIds = new Set(existingNodes.map(n => n.id));
  
  // 外向きリンク: 他章への参照ノードを作成
  const outgoingLinks = getOutgoingLinks(links, currentSection);
  console.log(`Found ${outgoingLinks.length} outgoing links for section ${currentSection}:`, outgoingLinks);
  
  outgoingLinks.forEach(link => {
    const virtualNodeId = `external_${link.target_section}_${link.target_concept}`;
    
    if (!existingNodeIds.has(virtualNodeId)) {
      virtualNodes.push({
        id: virtualNodeId,
        label: `${link.target_concept}`,
        tier: 'external',
        definition: `他章(${link.target_section})の概念: ${link.relation_description}`,
        aliases: [],
        evidence: [],
        external_reference: {
          section: link.target_section,
          original_concept: link.target_concept,
          confidence: link.confidence,
          pattern: link.pattern
        }
      });
      
      existingNodeIds.add(virtualNodeId);
    }
    
    // 現在のセクションの概念から外部参照ノードへのエッジ
    const sourceNodeId = existingNodes.find(n => 
      n.label === link.source_concept || n.id === link.source_concept
    )?.id;
    
    if (sourceNodeId) {
      crossEdges.push({
        source: sourceNodeId,
        target: virtualNodeId,
        relation: link.relation,
        relation_description: link.relation_description,
        confidence: link.confidence,
        evidence: [`章間リンク: ${link.source_section} → ${link.target_section}`],
        cross_chapter: true,
        target_section: link.target_section
      });
    }
  });

  // 内向きリンク: 他章から現在の章への参照ノードを作成
  const incomingLinks = getIncomingLinks(links, currentSection);
  console.log(`Found ${incomingLinks.length} incoming links for section ${currentSection}:`, incomingLinks);
  
  incomingLinks.forEach(link => {
    const virtualNodeId = `external_${link.source_section}_${link.source_concept}`;
    
    if (!existingNodeIds.has(virtualNodeId)) {
      virtualNodes.push({
        id: virtualNodeId,
        label: `${link.source_concept}`,
        tier: 'external',
        definition: `他章(${link.source_section})の概念: ${link.relation_description}`,
        aliases: [],
        evidence: [],
        external_reference: {
          section: link.source_section,
          original_concept: link.source_concept,
          confidence: link.confidence,
          pattern: link.pattern
        }
      });
      
      existingNodeIds.add(virtualNodeId);
    }
    
    // 外部参照ノードから現在のセクションの概念へのエッジ
    const targetNodeId = existingNodes.find(n => 
      n.label === link.target_concept || n.id === link.target_concept
    )?.id;
    
    if (targetNodeId) {
      crossEdges.push({
        source: virtualNodeId,
        target: targetNodeId,
        relation: link.relation,
        relation_description: link.relation_description,
        confidence: link.confidence,
        evidence: [`章間リンク: ${link.source_section} → ${link.target_section}`],
        cross_chapter: true,
        target_section: link.source_section
      });
    }
  });
  
  return { virtualNodes, crossEdges };
};

/**
 * セクションIDを表示用ラベルに変換
 */
export const getSectionLabel = (sectionId: string): string => {
  const sectionLabels: Record<string, string> = {
    '0-2': '0-2 自分の道を見つける',
    '1-0': '1-0 多元性を見る',
    '2-0': '2-0 ITと民主主義 拡大する溝',
    '2-1': '2-1 玉山からの眺め',
    '2-2': '2-2 デジタル民主主義の日常',
    '3-0': '3-0 プルラリティ（多元性）とは？',
    '3-1': '3-1 ⿻世界に生きる',
    '3-2': '3-2 つながった社会',
    '3-3': '3-3 失われた道',
    '4-0': '4-0 権利、オペレーティングシステム、的自由',
    '4-1': '4-1 IDと人物性',
    '4-2': '4-2 団体と公衆',
    '4-3': '4-3 商取引と信頼',
    '4-4': '4-4 財産と契約',
    '4-5': '4-5 アクセス',
    '5-0': '5-0 協働テクノロジーと民主主義',
    '5-1': '5-1 ポスト表象コミュニケーション',
    '5-2': '5-2 没入型共有現実（ISR）',
    '5-3': '5-3 クリエイティブなコラボレーション',
    '5-4': '5-4 拡張熟議',
    '5-5': '5-5 適応型管理行政',
    '5-6': '5-6 ⿻投票',
    '5-7': '5-7 社会市場',
    '6-0': '6-0  から現実へ',
    '6-1': '6-1 職場',
    '6-2': '6-2 保健',
    '6-3': '6-3 メディア',
    '6-4': '6-4 環境',
    '6-5': '6-5 学習',
    '7-0': '7-0 政策',
    '7-1': '7-1 結論'
  };
  
  return sectionLabels[sectionId] || sectionId;
};