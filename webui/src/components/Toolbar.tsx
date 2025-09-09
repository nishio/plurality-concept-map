import React from 'react';

interface ToolbarProps {
  selectedSection: string;
  onSectionChange: (section: string) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ selectedSection, onSectionChange }) => {
  const sections = [
    { value: '', label: 'セクション3-0（デフォルト）' },
    { value: 'sec3-1', label: 'セクション3-1' },
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