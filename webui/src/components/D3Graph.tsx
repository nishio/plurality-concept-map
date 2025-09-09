import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import { GraphData, Concept, Edge, D3Node, D3Link } from '../types';

interface D3GraphProps {
  data: GraphData;
  onNodeSelect: (concept: Concept) => void;
  onEdgeSelect: (edge: Edge) => void;
  selectedConcept?: Concept | null;
  selectedEdge?: Edge | null;
}

export const D3Graph: React.FC<D3GraphProps> = ({ data, onNodeSelect, onEdgeSelect, selectedConcept, selectedEdge }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [hasUserSelected, setHasUserSelected] = useState(false);
  const selectedNodeRef = useRef<D3Node | null>(null);
  const hasUserSelectedRef = useRef(false);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const transformRef = useRef<d3.ZoomTransform>(d3.zoomIdentity);

  const onNodeSelectRef = useRef(onNodeSelect);
  const onEdgeSelectRef = useRef(onEdgeSelect);

  // Update refs when callbacks change
  useEffect(() => {
    onNodeSelectRef.current = onNodeSelect;
    onEdgeSelectRef.current = onEdgeSelect;
  }, [onNodeSelect, onEdgeSelect]);

  const handleNodeSelect = useCallback((concept: Concept) => {
    onNodeSelectRef.current(concept);
  }, []);

  const handleEdgeSelect = useCallback((edge: Edge) => {
    onEdgeSelectRef.current(edge);
  }, []);

  const processedData = useMemo(() => {
    const nodes: D3Node[] = data.nodes.map(d => ({ ...d }));
    const id2node = new Map(nodes.map(d => [d.id, d]));
    const links: D3Link[] = data.edges.map(e => ({
      ...e,
      source: id2node.get(e.source)!,
      target: id2node.get(e.target)!
    }));
    return { nodes, links, id2node };
  }, [data]);

  // Helper function to update highlights
  const updateHighlights = useCallback(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const nodes = svg.selectAll('.node');
    const links = svg.selectAll('.link');
    const edgeLabels = svg.selectAll('.edge-label');

    // Reset all highlights
    nodes.classed('highlighted', false).classed('dimmed', false);
    links.classed('highlighted', false).classed('dimmed', false);
    edgeLabels.classed('highlighted', false).classed('dimmed', false);

    if (selectedConcept) {
      // Only highlight the selected concept node itself
      nodes.classed('highlighted', (d: any) => d.id === selectedConcept.id)
           .classed('dimmed', (d: any) => d.id !== selectedConcept.id);
    } else if (selectedEdge) {
      // Highlight selected edge and its nodes
      const sourceId = typeof selectedEdge.source === 'string' ? selectedEdge.source : selectedEdge.source.id;
      const targetId = typeof selectedEdge.target === 'string' ? selectedEdge.target : selectedEdge.target.id;
      
      nodes.classed('highlighted', (d: any) => d.id === sourceId || d.id === targetId)
           .classed('dimmed', (d: any) => d.id !== sourceId && d.id !== targetId);
      
      links.classed('highlighted', (d: any) => 
        (d.source.id === sourceId && d.target.id === targetId) ||
        (d.source.id === targetId && d.target.id === sourceId))
           .classed('dimmed', (d: any) => 
        !((d.source.id === sourceId && d.target.id === targetId) ||
          (d.source.id === targetId && d.target.id === sourceId)));
      
      edgeLabels.classed('highlighted', (d: any) => 
        (d.source.id === sourceId && d.target.id === targetId) ||
        (d.source.id === targetId && d.target.id === sourceId))
                .classed('dimmed', (d: any) => 
        !((d.source.id === sourceId && d.target.id === targetId) ||
          (d.source.id === targetId && d.target.id === sourceId)));
    }
  }, [selectedConcept, selectedEdge, data]);

  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const container = d3.select(containerRef.current);
    const containerRect = container.node()?.getBoundingClientRect();
    if (!containerRect) return;

    const width = containerRect.width;
    const height = containerRect.height;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    const g = svg.append('g');


    const linkG = g.append('g');
    const labelG = g.append('g');
    const nodeG = g.append('g');

    // Use processed data
    const { nodes, links } = processedData;

    // Create elements
    const link = linkG.selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('class', 'link');

    const edgeLabel = labelG.selectAll('text')
      .data(links)
      .enter()
      .append('text')
      .attr('class', 'edge-label')
      .text(d => d.relation || d.type)
      .style('cursor', 'pointer')
      .on('click', function(event, d) {
        event.stopPropagation();
        hasUserSelectedRef.current = true;
        setHasUserSelected(true); // Mark as user-selected
        handleEdgeSelect(d);
      });

    const node = nodeG.selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', d => `node ${d.tier || 'core'}`);

    node.append('circle')
      .attr('r', d => (d.tier === 'core' || !d.tier) ? 12 : (d.tier === 'supplementary' ? 10 : 8));

    node.append('text')
      .attr('dx', 16)
      .attr('dy', 4)
      .text(d => d.label);

    // Tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('display', 'none');

    // Selection handling
    const selectNode = function(event: any, d: D3Node) {
      node.classed('selected', false);
      selectedNodeRef.current = d;
      d3.select(this as any).classed('selected', true);
      handleNodeSelect(d);
      if (event) {
        hasUserSelectedRef.current = true;
        setHasUserSelected(true); // Mark as user-selected if event exists
      }
    };

    // Node interactions
    node.on('click', selectNode)
      .on('mouseover', (event, d) => {
        if (selectedNodeRef.current !== d) {
          tooltip.style('display', 'block')
            .html(`<strong>${d.label}</strong><br/>${d.definition || ''}<br/><em>${d.tier || 'core'}</em>`);
        }
      })
      .on('mousemove', (event) => {
        tooltip.style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY + 10) + 'px');
      })
      .on('mouseout', () => tooltip.style('display', 'none'));

    // Simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100).strength(0.5))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    simulation.on('tick', () => {
      link.attr('x1', (d: any) => d.source.x)
          .attr('y1', (d: any) => d.source.y)
          .attr('x2', (d: any) => d.target.x)
          .attr('y2', (d: any) => d.target.y);
          
      edgeLabel.attr('x', (d: any) => (d.source.x + d.target.x) / 2)
               .attr('y', (d: any) => (d.source.y + d.target.y) / 2 - 5);
               
      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag behavior
    node.call(d3.drag<any, any>()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }));

    // Zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        transformRef.current = event.transform; // Save transform state
      });

    // Store zoom for zoom controls
    zoomRef.current = zoom;
    svg.call(zoom);
    
    // Restore previous transform state
    if (transformRef.current && !transformRef.current.toString().includes('1,0,0,1,0,0')) {
      svg.call(zoom.transform, transformRef.current);
    }

    // Auto-select first core concept (including nodes without tier) only if user hasn't made a selection
    const firstCore = nodes.find(d => d.tier === 'core' || !d.tier);
    if (firstCore && !hasUserSelectedRef.current) {
      setTimeout(() => {
        const firstCoreNode = node.filter(d => d === firstCore);
        if (!firstCoreNode.empty()) {
          selectNode.call(firstCoreNode.node(), null, firstCore);
        }
      }, 100);
    }


    // Apply initial highlights
    updateHighlights();

    // Cleanup tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [processedData, updateHighlights]);

  // Update highlights when selection changes
  useEffect(() => {
    updateHighlights();
  }, [updateHighlights]);

  return (
    <div ref={containerRef} id="graph-container">
      <svg ref={svgRef} id="graph"></svg>
      <div className="zoom-controls">
        <div className="zoom-btn" onClick={() => {
          const svg = d3.select(svgRef.current!);
          if (zoomRef.current) {
            svg.transition().call(zoomRef.current.scaleBy, 1.5);
          }
        }}>+</div>
        <div className="zoom-btn" onClick={() => {
          const svg = d3.select(svgRef.current!);
          if (zoomRef.current) {
            svg.transition().call(zoomRef.current.scaleBy, 0.67);
          }
        }}>−</div>
        <div className="zoom-btn" style={{ fontSize: '12px' }} onClick={() => {
          const svg = d3.select(svgRef.current!);
          if (zoomRef.current) {
            svg.transition().call(zoomRef.current.transform, d3.zoomIdentity);
          }
        }}>⌂</div>
      </div>
    </div>
  );
};