import { GraphData } from '../types';

export const loadGraphData = async (dataUrl?: string): Promise<GraphData> => {
  if (dataUrl) {
    try {
      const response = await fetch(dataUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch data from ${dataUrl}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to load graph data:', error);
      throw error;
    }
  }
  
  // Fallback: try to load from graph.json in public directory
  try {
    const response = await fetch('./graph.json');
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.warn('No graph.json found, using sample data');
  }
  
  // Return empty data structure
  return { nodes: [], edges: [] };
};