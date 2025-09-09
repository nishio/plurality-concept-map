import React, { useState, useEffect } from 'react';
import { Toolbar } from './components/Toolbar';
import { ConceptDetails } from './components/ConceptDetails';
import { D3Graph } from './components/D3Graph';
import { GraphData, Concept, Edge } from './types';
import { sampleData } from './data/sample';
import { loadGraphData } from './utils/dataLoader';
import './App.css';

function App() {
  const [data, setData] = useState<GraphData>(sampleData);
  const [loading, setLoading] = useState(true);
  const [selectedConcept, setSelectedConcept] = useState<Concept | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);

  const handleNodeSelect = (concept: Concept) => {
    setSelectedConcept(concept);
    setSelectedEdge(null); // Clear edge selection when selecting node
  };

  const handleEdgeSelect = (edge: Edge) => {
    setSelectedEdge(edge);
    setSelectedConcept(null); // Clear node selection when selecting edge
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
        <Toolbar />
        <ConceptDetails concept={selectedConcept} edge={selectedEdge} data={data} onConceptSelect={handleNodeSelect} onEdgeSelect={handleEdgeSelect} />
      </div>
      
      <D3Graph 
        data={data} 
        onNodeSelect={handleNodeSelect}
        onEdgeSelect={handleEdgeSelect}
        selectedConcept={selectedConcept}
        selectedEdge={selectedEdge}
      />
    </div>
  );
}

export default App;