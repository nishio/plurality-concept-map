import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import * as d3 from 'd3';
import { GraphData, Concept, D3Node, D3Link, TierFilter } from '../types';

interface D3GraphProps {
  data: GraphData;
  filters: TierFilter;
  onNodeSelect: (concept: Concept) => void;
}

export const D3Graph: React.FC<D3GraphProps> = ({ data, filters, onNodeSelect }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<D3Node | null>(null);

  const handleNodeSelect = useCallback((concept: Concept) => {
    onNodeSelect(concept);
  }, [onNodeSelect]);

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

    // Arrow marker
    svg.append('defs').append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#64748b');

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
      .text(d => d.type);

    const node = nodeG.selectAll('g')
      .data(nodes)
      .enter()
      .append('g')
      .attr('class', d => `node ${d.tier}`);

    node.append('circle')
      .attr('r', d => d.tier === 'core' ? 12 : (d.tier === 'supplementary' ? 10 : 8));

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
      setSelectedNode(d);
      d3.select(this as any).classed('selected', true);
      handleNodeSelect(d);
    };

    // Node interactions
    node.on('click', selectNode)
      .on('mouseover', (event, d) => {
        if (selectedNode !== d) {
          tooltip.style('display', 'block')
            .html(`<strong>${d.label}</strong><br/>${d.definition || ''}<br/><em>${d.tier}</em>`);
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
      .on('zoom', (event) => g.attr('transform', event.transform));

    svg.call(zoom);

    // Auto-select first core concept
    const firstCore = nodes.find(d => d.tier === 'core');
    if (firstCore) {
      setTimeout(() => {
        const firstCoreNode = node.filter(d => d === firstCore);
        if (!firstCoreNode.empty()) {
          selectNode.call(firstCoreNode.node(), null, firstCore);
        }
      }, 100);
    }

    // Apply filters
    const applyFilters = () => {
      node.style('display', (d: D3Node) => {
        return (d.tier === 'core' && filters.core) || 
               (d.tier === 'supplementary' && filters.supplementary) || 
               (d.tier === 'advanced' && filters.advanced) ? null : 'none';
      });
      
      const visible = new Set<string>();
      node.filter(function() { 
        return d3.select(this).style('display') !== 'none'; 
      }).each((d: D3Node) => visible.add(d.id));
      
      link.style('display', (e: D3Link) => {
        return (visible.has(e.source.id) && visible.has(e.target.id)) ? null : 'none';
      });
      
      edgeLabel.style('display', (e: D3Link) => {
        return (visible.has(e.source.id) && visible.has(e.target.id)) ? null : 'none';
      });
    };

    applyFilters();

    // Cleanup tooltip on unmount
    return () => {
      tooltip.remove();
    };
  }, [processedData, filters, handleNodeSelect]);

  return (
    <div ref={containerRef} id="graph-container">
      <svg ref={svgRef} id="graph"></svg>
      <div className="zoom-controls">
        <div className="zoom-btn" onClick={() => {
          const svg = d3.select(svgRef.current!);
          svg.transition().call(d3.zoom<SVGSVGElement, unknown>().scaleBy, 1.5);
        }}>+</div>
        <div className="zoom-btn" onClick={() => {
          const svg = d3.select(svgRef.current!);
          svg.transition().call(d3.zoom<SVGSVGElement, unknown>().scaleBy, 0.67);
        }}>−</div>
        <div className="zoom-btn" style={{ fontSize: '12px' }} onClick={() => {
          const svg = d3.select(svgRef.current!);
          svg.transition().call(d3.zoom<SVGSVGElement, unknown>().transform, d3.zoomIdentity);
        }}>⌂</div>
      </div>
    </div>
  );
};