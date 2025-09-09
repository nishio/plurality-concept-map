import React from 'react';
import { Concept, Edge, GraphData } from '../types';

interface ConceptDetailsProps {
  concept: Concept | null;
  edge: Edge | null;
  data?: GraphData;
  onConceptSelect?: (concept: Concept) => void;
  onEdgeSelect?: (edge: Edge) => void;
}

export const ConceptDetails: React.FC<ConceptDetailsProps> = ({ concept, edge, data, onConceptSelect, onEdgeSelect }) => {
  if (!concept && !edge) {
    return (
      <div id="details">
        <div className="section-title">概念または関係を選択してください</div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
          グラフ内のノードまたはエッジラベルをクリックすると、詳細情報と証拠が表示されます。
        </p>
      </div>
    );
  }

  if (edge) {
    try {
      return (
        <div id="details">
          <div className="concept-card">
            <div className="concept-header">
              <span className="concept-tier tier-edge">関係</span>
              <h2 className="concept-title">{edge.relation_description || edge.relation || edge.type || '関係'}</h2>
            </div>

            {/* 関連概念の表示 */}
            {data && (
              <div className="related-concepts-section">
                <div className="section-title">関連概念</div>
                <div className="related-concepts">
                  {/* 元の概念 */}
                  {(() => {
                    const sourceId = typeof edge.source === 'string' ? edge.source : edge.source?.id;
                    const sourceConcept = data.nodes.find(node => node.id === sourceId);
                    return sourceConcept ? (
                      <div 
                        className="related-concept clickable" 
                        onClick={() => onConceptSelect && onConceptSelect(sourceConcept)}
                      >
                        <div className="concept-name">{sourceConcept.label}</div>
                        <div className="concept-def">{sourceConcept.definition}</div>
                      </div>
                    ) : null;
                  })()}
                  
                  {/* 先の概念 */}
                  {(() => {
                    const targetId = typeof edge.target === 'string' ? edge.target : edge.target?.id;
                    const targetConcept = data.nodes.find(node => node.id === targetId);
                    return targetConcept ? (
                      <div 
                        className="related-concept clickable" 
                        onClick={() => onConceptSelect && onConceptSelect(targetConcept)}
                      >
                        <div className="concept-name">{targetConcept.label}</div>
                        <div className="concept-def">{targetConcept.definition}</div>
                      </div>
                    ) : null;
                  })()}
                </div>
              </div>
            )}

            {edge.evidence && edge.evidence.length > 0 && (
              <div className="evidence-section">
                <div className="section-title">根拠・引用</div>
                {edge.evidence.map((e, index) => (
                  <div key={index} className="evidence-item">{e?.text || '証拠なし'}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      );
    } catch (error) {
      console.error('Error rendering edge details:', error);
      return (
        <div id="details">
          <div className="section-title">エラー</div>
          <p>関係情報の表示中にエラーが発生しました。</p>
        </div>
      );
    }
  }

  const aliases = concept.aliases && concept.aliases.length > 0 ? concept.aliases : [];
  const evidence = concept.evidence && concept.evidence.length > 0 ? concept.evidence : [];

  return (
    <div id="details">
      <div className="concept-card">
        <div className="concept-header">
          <span className="concept-tier tier-concept">概念</span>
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

        {/* 関係セクション */}
        {data && (
          <div className="relations-section">
            <div className="section-title">関係</div>
            <div className="relations">
              {data.edges
                .filter(edge => {
                  const sourceId = typeof edge.source === 'string' ? edge.source : edge.source?.id;
                  const targetId = typeof edge.target === 'string' ? edge.target : edge.target?.id;
                  return sourceId === concept.id || targetId === concept.id;
                })
                .map((edge, index) => {
                  const sourceId = typeof edge.source === 'string' ? edge.source : edge.source?.id;
                  const targetId = typeof edge.target === 'string' ? edge.target : edge.target?.id;
                  const isSource = sourceId === concept.id;
                  const relatedConceptId = isSource ? targetId : sourceId;
                  const relatedConcept = data.nodes.find(node => node.id === relatedConceptId);
                  
                  // 関係記述を作成（relation_descriptionがあれば使用、なければ構築）
                  const relationDescription = edge.relation_description || 
                    (relatedConcept ? 
                      `${concept.label}は${relatedConcept.label}を${edge.relation || edge.type}。` :
                      `${concept.label}は${relatedConceptId}を${edge.relation || edge.type}。`
                    );
                  
                  return (
                    <div 
                      key={index} 
                      className="relation-item clickable"
                      onClick={() => onEdgeSelect && onEdgeSelect(edge)}
                    >
                      <div className="relation-description">{relationDescription}</div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};