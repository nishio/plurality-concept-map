import React from 'react';
import { TierFilter } from '../types';

interface ToolbarProps {
  filters: TierFilter;
  onFilterChange: (filters: TierFilter) => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({ filters, onFilterChange }) => {
  const handleFilterChange = (tier: keyof TierFilter) => {
    onFilterChange({
      ...filters,
      [tier]: !filters[tier]
    });
  };

  return (
    <div id="toolbar">
      <h1>概念マップ</h1>
      <div className="filter-group">
        <label>
          <input 
            type="checkbox" 
            checked={filters.core}
            onChange={() => handleFilterChange('core')}
          /> 
          コア概念
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={filters.supplementary}
            onChange={() => handleFilterChange('supplementary')}
          /> 
          補助概念
        </label>
        <label>
          <input 
            type="checkbox" 
            checked={filters.advanced}
            onChange={() => handleFilterChange('advanced')}
          /> 
          発展概念
        </label>
      </div>
    </div>
  );
};