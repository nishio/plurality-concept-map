import React from 'react';
import { Concept } from '../types';

interface ConceptDetailsProps {
  concept: Concept | null;
}

export const ConceptDetails: React.FC<ConceptDetailsProps> = ({ concept }) => {
  if (!concept) {
    return (
      <div id="details">
        <div className="section-title">概念を選択してください</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
          グラフ内のノードをクリックすると、詳細情報と証拠が表示されます。
        </p>
      </div>
    );
  }

  const aliases = concept.aliases && concept.aliases.length > 0 ? concept.aliases : [];
  const evidence = concept.evidence && concept.evidence.length > 0 ? concept.evidence : [];

  return (
    <div id="details">
      <div className="concept-card">
        <div className="concept-header">
          <span className={`concept-tier tier-${concept.tier}`}>{concept.tier}</span>
          <h2 className="concept-title">{concept.label}</h2>
        </div>
        
        <div className="concept-definition">{concept.definition || '定義なし'}</div>

        {aliases.length > 0 && (
          <div className="aliases-section">
            <div className="section-title">別名・関連用語</div>
            <div className="aliases">
              {aliases.map((alias, index) => (
                <span key={index} className="alias-tag">{alias}</span>
              ))}
            </div>
          </div>
        )}

        {evidence.length > 0 && (
          <div className="evidence-section">
            <div className="section-title">根拠・引用</div>
            {evidence.map((e, index) => (
              <div key={index} className="evidence-item">{e.text}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};