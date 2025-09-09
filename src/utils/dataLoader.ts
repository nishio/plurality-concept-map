import { GraphData } from '../types';
import { sampleData } from '../data/sample';

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
  
  // Try to load from graph.json in public directory
  try {
    const response = await fetch('./graph.json');
    if (response.ok) {
      const data = await response.json();
      console.log('Loaded graph.json successfully');
      return data;
    }
  } catch (error) {
    console.warn('No graph.json found, using sample data');
  }
  
  // Fallback to sample data
  console.log('Using sample data');
  return sampleData;
};