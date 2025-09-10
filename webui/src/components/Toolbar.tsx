import React from 'react';

interface ToolbarProps {
  selectedSection: string;
  onSectionChange: (section: string) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ selectedSection, onSectionChange }) => {
  const sections = [
    { value: 'merged', label: '【全章統合】全体マップ' },
    { value: 'sec0-2', label: '0-2 自分の道を見つける' },
    { value: 'sec1-0', label: '1-0 多元性を見る' },
    { value: 'sec2-0', label: '2-0 ITと民主主義 拡大する溝' },
    { value: 'sec2-1', label: '2-1 玉山からの眺め' },
    { value: 'sec2-2', label: '2-2 デジタル民主主義の日常' },
    { value: 'sec3-0', label: '3-0 プルラリティ（多元性）とは？' },
    { value: 'sec3-1', label: '3-1 ⿻世界に生きる' },
    { value: 'sec3-2', label: '3-2 つながった社会' },
    { value: 'sec3-3', label: '3-3 失われた道' },
    { value: 'sec4-0', label: '4-0 権利、オペレーティングシステム、的自由' },
    { value: 'sec4-1', label: '4-1 IDと人物性' },
    { value: 'sec4-2', label: '4-2 団体と公衆' },
    { value: 'sec4-3', label: '4-3 商取引と信頼' },
    { value: 'sec4-4', label: '4-4 財産と契約' },
    { value: 'sec4-5', label: '4-5 アクセス' },
    { value: 'sec5-0', label: '5-0 協働テクノロジーと民主主義' },
    { value: 'sec5-1', label: '5-1 ポスト表象コミュニケーション' },
    { value: 'sec5-2', label: '5-2 没入型共有現実（ISR）' },
    { value: 'sec5-3', label: '5-3 クリエイティブなコラボレーション' },
    { value: 'sec5-4', label: '5-4 拡張熟議' },
    { value: 'sec5-5', label: '5-5 適応型管理行政' },
    { value: 'sec5-6', label: '5-6 ⿻投票' },
    { value: 'sec5-7', label: '5-7 社会市場' },
    { value: 'sec6-0', label: '6-0  から現実へ' },
    { value: 'sec6-1', label: '6-1 職場' },
    { value: 'sec6-2', label: '6-2 保健' },
    { value: 'sec6-3', label: '6-3 メディア' },
    { value: 'sec6-4', label: '6-4 環境' },
    { value: 'sec6-5', label: '6-5 学習' },
    { value: 'sec7-0', label: '7-0 政策' },
    { value: 'sec7-1', label: '7-1 結論' },
  ];

  return (
    <div id="toolbar">
      <h1>Plurality本の概念マップ</h1>
      <div className="section-selector">
        <label htmlFor="section-select">セクション選択:</label>
        <select 
          id="section-select" 
          value={selectedSection} 
          onChange={(e) => onSectionChange(e.target.value)}
        >
          {sections.map(section => (
            <option key={section.value} value={section.value}>
              {section.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};