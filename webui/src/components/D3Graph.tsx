import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import { GraphData, Concept, Edge, D3Node, D3Link } from '../types';

interface D3GraphProps {
  data: GraphData;
  onNodeSelect: (concept: Concept) => void;
  onEdgeSelect: (edge: Edge) => void;
  selectedConcept?: Concept | null;
  selectedEdge?: Edge | null;
}

export const D3Graph: React.FC<D3GraphProps> = ({ 
  data, 
  onNodeSelect, 
  onEdgeSelect, 
  selectedConcept, 
  selectedEdge 
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const simulationRef = useRef<d3.Simulation<D3Node, D3Link> | null>(null);
  const zoomRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const transformRef = useRef<d3.ZoomTransform>(d3.zoomIdentity);
  const tooltipRef = useRef<d3.Selection<HTMLDivElement, unknown, HTMLElement, any> | null>(null);

  // Process data into D3 format
  const processedData = useMemo(() => {
    const nodes: D3Node[] = data.nodes.map(d => ({ ...d }));
    const id2node = new Map(nodes.map(d => [d.id, d]));
    const links: D3Link[] = data.edges.map(e => ({
      ...e,
      source: id2node.get(e.source)!,
      target: id2node.get(e.target)!
    }));
    return { nodes, links };
  }, [data]);

  // Initialize tooltip once
  useEffect(() => {
    if (!tooltipRef.current) {
      tooltipRef.current = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .style('display', 'none');
    }
    
    return () => {
      tooltipRef.current?.remove();
      tooltipRef.current = null;
    };
  }, []);

  // Main D3 graph setup and update
  useEffect(() => {
    if (!svgRef.current || !containerRef.current) return;

    const container = containerRef.current;
    const { width, height } = container.getBoundingClientRect();
    
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height);

    // Setup main group for zooming
    let g = svg.select<SVGGElement>('g.main-group');
    if (g.empty()) {
      g = svg.append('g').attr('class', 'main-group');
    }

    // Setup zoom behavior
    if (!zoomRef.current) {
      zoomRef.current = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.3, 3])
        .on('zoom', (event) => {
          g.attr('transform', event.transform);
          transformRef.current = event.transform;
        });
      
      svg.call(zoomRef.current);
      
      // Restore previous transform if exists
      if (transformRef.current.k !== 1 || transformRef.current.x !== 0 || transformRef.current.y !== 0) {
        svg.call(zoomRef.current.transform, transformRef.current);
      }
    }

    // Setup groups
    let linkG = g.select<SVGGElement>('g.links');
    let labelG = g.select<SVGGElement>('g.labels');
    let nodeG = g.select<SVGGElement>('g.nodes');
    
    if (linkG.empty()) linkG = g.append('g').attr('class', 'links');
    if (labelG.empty()) labelG = g.append('g').attr('class', 'labels');
    if (nodeG.empty()) nodeG = g.append('g').attr('class', 'nodes');

    const { nodes, links } = processedData;

    // Data binding with proper enter/update/exit pattern for links
    const linkSelection = linkG.selectAll<SVGLineElement, D3Link>('line')
      .data(links, d => `${(d.source as D3Node).id}-${(d.target as D3Node).id}`);

    linkSelection.exit().remove();

    const linkEnter = linkSelection.enter()
      .append('line')
      .attr('class', d => d.cross_chapter ? 'link cross-chapter' : 'link');

    const linkUpdate = linkEnter.merge(linkSelection);

    // Data binding for edge labels
    const labelSelection = labelG.selectAll<SVGTextElement, D3Link>('text')
      .data(links, d => `${(d.source as D3Node).id}-${(d.target as D3Node).id}`);

    labelSelection.exit().remove();

    const labelEnter = labelSelection.enter()
      .append('text')
      .attr('class', 'edge-label')
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        onEdgeSelect(d);
      });

    const labelUpdate = labelEnter.merge(labelSelection)
      .text(d => d.relation || d.type || '');

    // Data binding for nodes
    const nodeSelection = nodeG.selectAll<SVGGElement, D3Node>('g.node')
      .data(nodes, d => d.id);

    nodeSelection.exit().remove();

    const nodeEnter = nodeSelection.enter()
      .append('g')
      .attr('class', d => `node ${d.tier || 'core'}`);

    nodeEnter.append('circle')
      .attr('r', d => {
        if (d.tier === 'core' || !d.tier) return 12;
        if (d.tier === 'supplementary') return 10;
        if (d.tier === 'external') return 10;
        return 8;
      });

    nodeEnter.append('text')
      .attr('dx', 16)
      .attr('dy', 4);

    const nodeUpdate = nodeEnter.merge(nodeSelection);
    
    // Update node text
    nodeUpdate.select('text')
      .text(d => d.label);

    // Setup node interactions
    nodeUpdate
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        onNodeSelect(d);
      })
      .on('mouseover', (event, d) => {
        if (tooltipRef.current && d.id !== selectedConcept?.id) {
          tooltipRef.current
            .style('display', 'block')
            .html(`<strong>${d.label}</strong><br/>${d.definition || ''}<br/><em>${d.tier || 'core'}</em>`);
        }
      })
      .on('mousemove', (event) => {
        if (tooltipRef.current) {
          tooltipRef.current
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY + 10) + 'px');
        }
      })
      .on('mouseout', () => {
        if (tooltipRef.current) {
          tooltipRef.current.style('display', 'none');
        }
      });

    // Setup or update simulation
    if (!simulationRef.current) {
      simulationRef.current = d3.forceSimulation<D3Node>(nodes)
        .force('link', d3.forceLink<D3Node, D3Link>(links)
          .id(d => d.id)
          .distance(100)
          .strength(0.5))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));
    } else {
      // Update existing simulation with new data
      simulationRef.current.nodes(nodes);
      const linkForce = simulationRef.current.force<d3.ForceLink<D3Node, D3Link>>('link');
      if (linkForce) {
        linkForce.links(links);
      }
      simulationRef.current.alpha(0.3).restart();
    }

    // Update positions on tick
    simulationRef.current.on('tick', () => {
      linkUpdate
        .attr('x1', d => (d.source as D3Node).x!)
        .attr('y1', d => (d.source as D3Node).y!)
        .attr('x2', d => (d.target as D3Node).x!)
        .attr('y2', d => (d.target as D3Node).y!);

      labelUpdate
        .attr('x', d => ((d.source as D3Node).x! + (d.target as D3Node).x!) / 2)
        .attr('y', d => ((d.source as D3Node).y! + (d.target as D3Node).y!) / 2 - 5);

      nodeUpdate
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Setup drag behavior
    const drag = d3.drag<SVGGElement, D3Node>()
      .on('start', (event, d) => {
        if (!event.active) simulationRef.current?.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulationRef.current?.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    nodeUpdate.call(drag);

    // Cleanup on unmount
    return () => {
      simulationRef.current?.stop();
    };
  }, [processedData, onNodeSelect, onEdgeSelect]);

  // Update highlights based on selection (props-driven)
  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const nodes = svg.selectAll<SVGGElement, D3Node>('g.node');
    const links = svg.selectAll<SVGLineElement, D3Link>('.link');
    const labels = svg.selectAll<SVGTextElement, D3Link>('.edge-label');

    // Reset all styles
    nodes.classed('highlighted', false).classed('dimmed', false).classed('selected', false);
    links.classed('highlighted', false).classed('dimmed', false);
    labels.classed('highlighted', false).classed('dimmed', false);

    if (selectedConcept) {
      // Highlight selected concept
      nodes
        .classed('selected', d => d.id === selectedConcept.id)
        .classed('highlighted', d => d.id === selectedConcept.id)
        .classed('dimmed', d => d.id !== selectedConcept.id);
        
    } else if (selectedEdge) {
      // Highlight selected edge and its connected nodes
      const sourceId = typeof selectedEdge.source === 'string' 
        ? selectedEdge.source 
        : (selectedEdge.source as D3Node).id;
      const targetId = typeof selectedEdge.target === 'string' 
        ? selectedEdge.target 
        : (selectedEdge.target as D3Node).id;

      nodes
        .classed('highlighted', d => d.id === sourceId || d.id === targetId)
        .classed('dimmed', d => d.id !== sourceId && d.id !== targetId);

      links
        .classed('highlighted', d => {
          const linkSourceId = (d.source as D3Node).id;
          const linkTargetId = (d.target as D3Node).id;
          return (linkSourceId === sourceId && linkTargetId === targetId) ||
                 (linkSourceId === targetId && linkTargetId === sourceId);
        })
        .classed('dimmed', d => {
          const linkSourceId = (d.source as D3Node).id;
          const linkTargetId = (d.target as D3Node).id;
          return !((linkSourceId === sourceId && linkTargetId === targetId) ||
                   (linkSourceId === targetId && linkTargetId === sourceId));
        });

      labels
        .classed('highlighted', d => {
          const linkSourceId = (d.source as D3Node).id;
          const linkTargetId = (d.target as D3Node).id;
          return (linkSourceId === sourceId && linkTargetId === targetId) ||
                 (linkSourceId === targetId && linkTargetId === sourceId);
        })
        .classed('dimmed', d => {
          const linkSourceId = (d.source as D3Node).id;
          const linkTargetId = (d.target as D3Node).id;
          return !((linkSourceId === sourceId && linkTargetId === targetId) ||
                   (linkSourceId === targetId && linkTargetId === sourceId));
        });
    }
  }, [selectedConcept, selectedEdge]);

  // Handle zoom controls
  const handleZoomIn = useCallback(() => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current).transition().call(zoomRef.current.scaleBy, 1.5);
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current).transition().call(zoomRef.current.scaleBy, 0.67);
    }
  }, []);

  const handleZoomReset = useCallback(() => {
    if (svgRef.current && zoomRef.current) {
      d3.select(svgRef.current).transition().call(zoomRef.current.transform, d3.zoomIdentity);
    }
  }, []);

  return (
    <div ref={containerRef} id="graph-container">
      <svg ref={svgRef} id="graph"></svg>
      <div className="zoom-controls">
        <div className="zoom-btn" onClick={handleZoomIn}>+</div>
        <div className="zoom-btn" onClick={handleZoomOut}>−</div>
        <div className="zoom-btn" style={{ fontSize: '12px' }} onClick={handleZoomReset}>⌂</div>
      </div>
    </div>
  );
};