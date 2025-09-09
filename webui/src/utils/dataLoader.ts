import { GraphData } from '../types';
import { sampleData } from '../data/sample';

export const loadGraphData = async (section?: string): Promise<GraphData> => {
  // Determine which file to load based on section
  const fileName = section ? `graph_${section}.json` : 'graph_sec3-0.json';
  
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
  
  // If specified section file not found, try fallback options
  if (section) {
    // Try the default sec3-0 file
    try {
      const response = await fetch('./graph_sec3-0.json');
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded fallback graph_sec3-0.json successfully');
        return data;
      }
    } catch (error) {
      console.warn('No graph_sec3-0.json found either');
    }
  }
  
  // Fallback to sample data
  console.log('Using sample data');
  return sampleData;
};