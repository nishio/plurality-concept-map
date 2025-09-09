import { GraphData } from '../types';

const fallbackData: GraphData = {
  nodes: [
    {
      id: 'loading',
      label: 'データ読み込み中...',
      tier: 'core',
      definition: 'グラフデータが読み込まれるまでお待ちください',
      aliases: [],
      evidence: []
    }
  ],
  edges: []
};

export const loadGraphData = async (section?: string): Promise<GraphData> => {
  // Determine which file to load based on section
  const fileName = section ? `graph_${section}.json` : 'graph_sec1-0.json';
  
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
  if (section && section !== 'sec1-0') {
    // Try the default sec1-0 file
    try {
      const response = await fetch('./graph_sec1-0.json');
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded fallback graph_sec1-0.json successfully');
        return data;
      }
    } catch (error) {
      console.warn('No graph_sec1-0.json found either');
    }
  }
  
  // Fallback to minimal data
  console.log('Using fallback data - no graph files found');
  return fallbackData;
};