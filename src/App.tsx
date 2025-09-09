import React, { useState, useEffect } from 'react';
import { Toolbar } from './components/Toolbar';
import { ConceptDetails } from './components/ConceptDetails';
import { D3Graph } from './components/D3Graph';
import { GraphData, Concept, TierFilter } from './types';
import { sampleData } from './data/sample';
import { loadGraphData } from './utils/dataLoader';
import './App.css';

function App() {
  const [data, setData] = useState<GraphData>(sampleData);
  const [loading, setLoading] = useState(true);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [filters, setFilters] = useState<TierFilter>({
    core: true,
    supplementary: true,
    advanced: true
  });

  const handleNodeSelect = (concept: Concept) => {
    setSelectedConcept(concept);
  };

  const handleFilterChange = (newFilters: TierFilter) => {
    setFilters(newFilters);
  };

  useEffect(() => {
    const initializeData = async () => {
      try {
        const graphData = await loadGraphData();
        if (graphData.nodes.length > 0) {
          setData(graphData);
        }
      } catch (error) {
        console.warn('Using sample data due to error:', error);
      } finally {
        setLoading(false);
      }
    };

    initializeData();
  }, []);

  if (loading) {
    return (
      <div id="app" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div>Loading concept map...</div>
      </div>
    );
  }

  return (
    <div id="app">
      <div id="sidebar">
        <Toolbar filters={filters} onFilterChange={handleFilterChange} />
        <ConceptDetails concept={selectedConcept} />
      </div>
      
      <D3Graph 
        data={data} 
        filters={filters}
        onNodeSelect={handleNodeSelect}
      />
    </div>
  );
}

export default App;