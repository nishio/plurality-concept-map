import { Evidence } from '../types';

/**
 * セクションIDから原文URLを生成
 */
export const getSourceUrl = (
  sectionId: string,
  evidence?: Evidence,
  baseUrl?: string
): string | null => {
  // Extraセクションの専用URL処理
  if (sectionId.startsWith('extra-')) {
    const extraUrls: Record<string, string> = {
      'extra-1': 'https://cybozushiki.cybozu.co.jp/articles/m006262.html',
      'extra-2': 'https://cybozushiki.cybozu.co.jp/articles/m006261.html',
      'extra-3': 'https://wired.jp/article/what-is-plurality-book/'
    };
    
    const extraUrl = extraUrls[sectionId];
    if (extraUrl) {
      // テキストフラグメントの生成
      if (evidence?.text) {
        const textFragment = createTextFragment(evidence.text);
        return `${extraUrl}#:~:text=${textFragment}`;
      }
      return extraUrl;
    }
  }

  // デフォルトのベースURL（Plurality.net）
  const defaultBaseUrl = 'https://www.plurality.net/v/chapters';
  const url = baseUrl || defaultBaseUrl;
  
  // セクションIDのフォーマット確認（例: "3-0", "sec3-0"）
  const normalizedSection = sectionId.startsWith('sec') ? sectionId.substring(3) : sectionId;
  
  // Plurality.net用のURLパス生成
  if (!baseUrl || baseUrl.includes('plurality.net')) {
    // 特別なマッピング: 1-0 -> 1 (第1章は1-0ではなく1のパスを使用)
    let urlPath = normalizedSection;
    if (normalizedSection === '1-0') {
      urlPath = '1';
    }
    
    const chapterUrl = `${url}/${urlPath}/jpn/`;
    
    // テキストフラグメントの生成
    if (evidence?.text) {
      const textFragment = createTextFragment(evidence.text);
      return `${chapterUrl}#:~:text=${textFragment}`;
    }
    
    return chapterUrl;
  }
  
  // カスタムURLの場合（将来の拡張用）
  if (evidence?.source_url) {
    return evidence.source_url;
  }
  
  return null;
};

/**
 * テキストフラグメントを生成
 * 長いテキストの場合は開始と終了を使用
 */
export const createTextFragment = (text: string): string => {
  // 改行やスペースを正規化
  const normalizedText = text.trim().replace(/\s+/g, ' ');
  
  // 長いテキストの場合、開始と終了を抽出
  if (normalizedText.length > 100) {
    // 最初の20文字と最後の20文字を使用
    const words = normalizedText.split(' ');
    
    if (words.length > 10) {
      // 最初の5単語
      const startWords = words.slice(0, 5).join(' ');
      // 最後の5単語
      const endWords = words.slice(-5).join(' ');
      
      // URLエンコード
      const encodedStart = encodeURIComponent(startWords);
      const encodedEnd = encodeURIComponent(endWords);
      
      return `${encodedStart},${encodedEnd}`;
    }
  }
  
  // 短いテキストはそのままエンコード
  // 特殊文字をエスケープ
  const escaped = normalizedText
    .replace(/[.*+?^${}()|[\]\\]/g, '\\$&') // 正規表現特殊文字をエスケープ
    .substring(0, 300); // 最大300文字に制限
  
  return encodeURIComponent(escaped);
};

/**
 * 現在のセクションIDを取得
 * Note: This should be passed from the component as a prop rather than trying to read from DOM
 */
export const getCurrentSectionId = (): string | null => {
  // ツールバーのセレクタから取得
  const selector = document.getElementById('section-selector') as HTMLSelectElement;
  if (selector?.value) {
    return selector.value;
  }
  
  // デフォルト値
  return 'sec1-0';
};

/**
 * セクションIDから章番号と章タイトルを取得
 */
export const getSectionInfo = (sectionId: string): { chapter: string; title: string } => {
  const normalizedSection = sectionId.startsWith('sec') ? sectionId.substring(3) : sectionId;
  
  const sectionTitles: Record<string, string> = {
    '0-2': '自分の道を見つける',
    '1-0': '多元性を見る',
    '2-0': 'ITと民主主義 拡大する溝',
    '2-1': '玉山からの眺め',
    '2-2': 'デジタル民主主義の日常',
    '3-0': 'プルラリティ（多元性）とは？',
    '3-1': '⿻世界に生きる',
    '3-2': 'つながった社会',
    '3-3': '失われた道',
    '4-0': '権利、オペレーティングシステム、的自由',
    '4-1': 'IDと人物性',
    '4-2': '団体と公衆',
    '4-3': '商取引と信頼',
    '4-4': '財産と契約',
    '4-5': 'アクセス',
    '5-0': '協働テクノロジーと民主主義',
    '5-1': 'ポスト表象コミュニケーション',
    '5-2': '没入型共有現実（ISR）',
    '5-3': 'クリエイティブなコラボレーション',
    '5-4': '拡張熟議',
    '5-5': '適応型管理行政',
    '5-6': '⿻投票',
    '5-7': '社会市場',
    '6-0': ' から現実へ',
    '6-1': '職場',
    '6-2': '保健',
    '6-3': 'メディア',
    '6-4': '環境',
    '6-5': '学習',
    '7-0': '政策',
    '7-1': '結論'
  };
  
  return {
    chapter: normalizedSection,
    title: sectionTitles[normalizedSection] || normalizedSection
  };
};