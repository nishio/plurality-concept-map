export interface Evidence {
  text: string;
  section?: string;
}

export interface Concept {
  id: string;
  label: string;
  definition: string;
  tier: 'core' | 'supplementary' | 'advanced';
  aliases: string[];
  evidence: Evidence[];
}

export interface Edge {
  source: string;
  target: string;
  type?: string; // Legacy field, kept for backward compatibility
  relation?: string; // Short relation label for graph display
  relation_description?: string; // Full natural language description
  confidence: number;
  evidence: Evidence[];
}

export interface GraphData {
  nodes: Concept[];
  edges: Edge[];
}

export interface D3Node extends Concept {
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface D3Link extends Edge {
  source: D3Node;
  target: D3Node;
}

export type TierFilter = {
  core: boolean;
  supplementary: boolean;
  advanced: boolean;
};