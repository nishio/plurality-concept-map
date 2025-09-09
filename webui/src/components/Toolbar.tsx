import React from 'react';

interface ToolbarProps {
  selectedSection: string;
  onSectionChange: (section: string) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ selectedSection, onSectionChange }) => {
  const sections = [
    { value: '', label: '3-0 プルラリティ（多元性）とは？' },
    { value: 'sec3-1', label: '3-1 ⿻世界に生きる' },
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