import { GraphData } from '../types';
import { sampleData } from '../data/sample';

export const loadGraphData = async (section?: string): Promise<GraphData> => {
  // Determine which file to load based on section
  const fileName = section ? `graph_${section}.json` : 'graph.json';
  
  // Try to load the specified JSON file
  try {
    const response = await fetch(`./${fileName}`);
    if (response.ok) {
      const data = await response.json();
      console.log(`Loaded ${fileName} successfully`);
      return data;
    }
  } catch (error) {
    console.warn(`No ${fileName} found`);
  }
  
  // If specified section file not found, try default graph.json
  if (section) {
    try {
      const response = await fetch('./graph.json');
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded default graph.json successfully');
        return data;
      }
    } catch (error) {
      console.warn('No graph.json found either');
    }
  }
  
  // Fallback to sample data
  console.log('Using sample data');
  return sampleData;
};