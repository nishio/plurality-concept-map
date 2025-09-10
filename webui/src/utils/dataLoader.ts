import { GraphData } from '../types';
import { loadCrossChapterLinks, createCrossChapterNodes } from './crossChapterLinks';

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
  // Handle merged graph case
  if (section === 'merged') {
    try {
      const response = await fetch('./graph_merged.json');
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded graph_merged.json successfully');
        return data;
      }
    } catch (error) {
      console.warn('No graph_merged.json found');
    }
  }

  // Determine which file to load based on section
  const fileName = section ? `graph_${section}.json` : 'graph_sec1-0.json';
  let graphData: GraphData | null = null;
  
  // Try to load the specified JSON file
  try {
    const response = await fetch(`./${fileName}`);
    if (response.ok) {
      graphData = await response.json();
      console.log(`Loaded ${fileName} successfully`);
    }
  } catch (error) {
    console.warn(`No ${fileName} found`);
  }
  
  // If specified section file not found, try fallback options
  if (!graphData && section && section !== 'sec1-0') {
    // Try the default sec1-0 file
    try {
      const response = await fetch('./graph_sec1-0.json');
      if (response.ok) {
        graphData = await response.json();
        console.log('Loaded fallback graph_sec1-0.json successfully');
      }
    } catch (error) {
      console.warn('No graph_sec1-0.json found either');
    }
  }
  
  // If still no data, use fallback
  if (!graphData) {
    console.log('Using fallback data - no graph files found');
    return fallbackData;
  }

  // Add cross-chapter links if we have a specific section (not merged)
  if (section && section !== 'merged') {
    try {
      // Convert section format from 'sec3-0' to '3-0'
      const normalizedSection = section.startsWith('sec') ? section.substring(3) : section;
      console.log(`Loading cross-chapter links for section: ${section} (normalized: ${normalizedSection})`);
      
      const crossChapterData = await loadCrossChapterLinks();
      console.log('Cross-chapter data loaded:', crossChapterData);
      
      const { virtualNodes, crossEdges } = createCrossChapterNodes(
        crossChapterData.cross_chapter_links,
        normalizedSection,
        graphData.nodes
      );

      console.log(`Creating cross-chapter nodes for section ${section}:`, {
        virtualNodes: virtualNodes.length,
        crossEdges: crossEdges.length,
        sampleVirtualNode: virtualNodes[0],
        sampleCrossEdge: crossEdges[0]
      });

      // Merge virtual nodes and cross edges
      graphData = {
        nodes: [...graphData.nodes, ...virtualNodes],
        edges: [...graphData.edges, ...crossEdges]
      };
      
      console.log(`Added ${virtualNodes.length} external nodes and ${crossEdges.length} cross-chapter edges`);
    } catch (error) {
      console.error('Failed to add cross-chapter links:', error);
    }
  }
  
  return graphData;
};