// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { agents, workflowLines, connections, activeCampaigns } from '../data/workflows';
import './SubwayMap.css';

// Physics simulation parameters
const SIMULATION_DEFAULTS = {
  forceStrength: 0.3,         // Strength of the force
  linkDistance: 80,           // Distance between connected nodes
  chargeStrength: -400,       // Node repulsion strength (negative value)
  collisionRadius: 30,        // Minimum distance between nodes
  alpha: 0.3,                 // Starting force (0-1)
  alphaDecay: 0.02,           // How quickly the force reduces
  alphaMin: 0.001,            // Minimum force before simulation rests
  velocityDecay: 0.4,         // Friction coefficient
  centerForceX: 0.8,          // Strength of force pulling to center-x (0-1)
  centerForceY: 0.8,          // Strength of force pulling to center-y (0-1)
  groupingForceStrength: 0.4,  // Strength of grouping force by office type
};

const SubwayMap = () => {
  const svgRef = useRef(null);
  const simulationRef = useRef(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [selectedLine, setSelectedLine] = useState(null);
  const [hoveredAgent, setHoveredAgent] = useState(null);
  const [zoom, setZoom] = useState({ k: 1, x: 0, y: 0 });
  const [simulationParams, setSimulationParams] = useState(SIMULATION_DEFAULTS);
  const [isSimulationRunning, setIsSimulationRunning] = useState(true);
  const [nodesData, setNodesData] = useState([]);
  const [linksData, setLinksData] = useState([]);

  // Prepare data for force simulation
  useEffect(() => {
    // Create nodes data from agents
    const nodes = agents.map(agent => ({
      ...agent,
      // Keep original positions as starting positions
      x: agent.position.x,
      y: agent.position.y,
      // Add properties for simulation
      radius: 12,
      groupX: getGroupXPosition(agent.office),
      groupY: getGroupYPosition(agent.office)
    }));
    
    // Create links data from connections
    const links = connections.map(connection => ({
      ...connection,
      // Convert source and target from id to object reference (required by D3 force)
      source: connection.source,
      target: connection.target,
      // Add line color for rendering
      color: workflowLines.find(l => l.id === connection.lineId)?.color || '#999'
    }));
    
    setNodesData(nodes);
    setLinksData(links);
  }, []);
  
  // Function to determine x-position grouping by office type
  const getGroupXPosition = (office) => {
    const width = svgRef.current?.clientWidth || 1200;
    switch(office) {
      case 'front': return width * 0.2;
      case 'middle': return width * 0.5;
      case 'back': return width * 0.8;
      case 'executive': return width * 0.5;
      default: return width * 0.5;
    }
  };
  
  // Function to determine y-position grouping by office type
  const getGroupYPosition = (office) => {
    const height = svgRef.current?.clientHeight || 800;
    switch(office) {
      case 'executive': return height * 0.15;
      default: return height * 0.5; // All other offices spread vertically
    }
  };

  // Initialize and render the subway map
  useEffect(() => {
    if (!svgRef.current || nodesData.length === 0 || linksData.length === 0) return;

    // Clear any existing svg content
    d3.select(svgRef.current).selectAll("*").remove();

    // Create SVG and main group for zoom behavior
    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth || 1200;
    const height = svgRef.current.clientHeight || 800;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Set up zoom behavior
    const zoomBehavior = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        setZoom(event.transform);
        mainGroup.attr('transform', event.transform);
      });

    svg.call(zoomBehavior);

    // Create main group that will be transformed by zoom
    const mainGroup = svg.append('g')
      .attr('class', 'main-group')
      .attr('transform', `translate(${zoom.x},${zoom.y}) scale(${zoom.k})`);

    // Create groups for different elements
    const linesGroup = mainGroup.append('g').attr('class', 'lines-group');
    const connectionsGroup = mainGroup.append('g').attr('class', 'connections-group');
    const agentsGroup = mainGroup.append('g').attr('class', 'agents-group');
    const campaignsGroup = mainGroup.append('g').attr('class', 'campaigns-group');
    const labelsGroup = mainGroup.append('g').attr('class', 'labels-group');
    
    // Create force simulation
    const simulation = d3.forceSimulation(nodesData)
      .force('link', d3.forceLink(linksData)
        .id(d => d.id)
        .distance(simulationParams.linkDistance)
        .strength(simulationParams.forceStrength))
      .force('charge', d3.forceManyBody()
        .strength(simulationParams.chargeStrength))
      .force('collision', d3.forceCollide()
        .radius(simulationParams.collisionRadius))
      .force('x', d3.forceX(d => d.groupX).strength(simulationParams.centerForceX))
      .force('y', d3.forceY(d => d.groupY).strength(simulationParams.centerForceY))
      .alpha(simulationParams.alpha)
      .alphaDecay(simulationParams.alphaDecay)
      .alphaMin(simulationParams.alphaMin)
      .velocityDecay(simulationParams.velocityDecay);
    
    // Store simulation reference for controls
    simulationRef.current = simulation;

    // Draw connections (subway lines)
    const link = connectionsGroup.selectAll('.connection')
      .data(linksData)
      .enter()
      .append('path')
      .attr('stroke', d => d.color)
      .attr('stroke-width', 4)
      .attr('fill', 'none')
      .attr('class', d => `connection connection-${d.id} line-${d.lineId}`)
      .attr('data-source', d => d.source)
      .attr('data-target', d => d.target)
      .attr('data-line', d => d.lineId);

    // Draw agents (stations)
    const node = agentsGroup.selectAll('.agent-station')
      .data(nodesData)
      .enter()
      .append('g')
      .attr('class', d => `agent-station agent-${d.id} office-${d.office}`)
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on('click', (event, d) => {
        event.stopPropagation(); // Prevent triggering click on background
        setSelectedAgent(d);
      })
      .on('mouseover', (event, d) => {
        setHoveredAgent(d);
      })
      .on('mouseout', () => {
        setHoveredAgent(null);
      })
      .each(function(d) {
        // Main station circle
        d3.select(this)
          .append('circle')
          .attr('r', 12)
          .attr('fill', 'white')
          .attr('stroke', d.color)
          .attr('stroke-width', 3);
        
        // Office indicator (inner circle)
        d3.select(this)
          .append('circle')
          .attr('r', 8)
          .attr('fill', d.color);
      });
      
    // Add labels (separate from nodes for better control)
    const label = labelsGroup.selectAll('.agent-label')
      .data(nodesData)
      .enter()
      .append('text')
      .attr('class', 'agent-label')
      .attr('text-anchor', 'middle')
      .text(d => d.name);
      
    // Functions for drag behavior
    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    
    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }
    
    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      if (!isSimulationRunning) {
        d.fx = event.x;
        d.fy = event.y;
      } else {
        d.fx = null;
        d.fy = null;
      }
    }

    // Simulation tick function to update positions
    simulation.on('tick', () => {
      // Update connection paths
      link.attr('d', d => {
        const sourceNode = nodesData.find(n => n.id === d.source);
        const targetNode = nodesData.find(n => n.id === d.target);
        
        if (!sourceNode || !targetNode) return '';
        
        // Create a curved path between nodes
        const midX = (sourceNode.x + targetNode.x) / 2;
        const midY = (sourceNode.y + targetNode.y) / 2 - 20; // Curve upward slightly
        
        return `M${sourceNode.x},${sourceNode.y} Q${midX},${midY} ${targetNode.x},${targetNode.y}`;
      });
      
      // Update agent station positions
      node.attr('transform', d => `translate(${d.x}, ${d.y})`);
      
      // Update label positions
      label.attr('x', d => d.x)
           .attr('y', d => d.y + 25);
      
      // Update campaign positions
      updateCampaignPositions();
    });
    
    // Function to update campaign positions based on agent positions
    function updateCampaignPositions() {
      // Remove existing campaigns
      campaignsGroup.selectAll('*').remove();
      
      // Draw active campaigns (trains)
      activeCampaigns.forEach(campaign => {
        const line = workflowLines.find(l => l.id === campaign.lineId);
        const currentStationNode = nodesData.find(n => n.id === campaign.currentStationId);
        const nextStationNode = nodesData.find(n => n.id === campaign.nextStationId);
        
        if (!currentStationNode || !nextStationNode || !line) return;
        
        // Calculate position along the connection (based on progress)
        const progress = campaign.progress / 100;
        const campaignX = currentStationNode.x + (nextStationNode.x - currentStationNode.x) * progress;
        const campaignY = currentStationNode.y + (nextStationNode.y - currentStationNode.y) * progress;
        
        // Draw campaign train
        campaignsGroup.append('g')
          .attr('class', `campaign campaign-${campaign.id} priority-${campaign.priority}`)
          .attr('transform', `translate(${campaignX}, ${campaignY})`)
          .on('click', (event) => {
            event.stopPropagation();
            setSelectedCampaign(campaign);
          })
          .each(function() {
            // Train car
            d3.select(this)
              .append('rect')
              .attr('x', -8)
              .attr('y', -8)
              .attr('width', 16)
              .attr('height', 16)
              .attr('rx', 3)
              .attr('fill', line.color)
              .attr('stroke', 'white')
              .attr('stroke-width', 1);
            
            // Priority indicator
            if (campaign.priority <= 2) {
              d3.select(this)
                .append('circle')
                .attr('cx', 4)
                .attr('cy', -4)
                .attr('r', 3)
                .attr('fill', campaign.priority === 1 ? '#f44336' : '#ff9800');
            }
          });
      });
    }

    // Add legend for workflow lines
    const legendGroup = svg.append('g')
      .attr('class', 'legend')
      .attr('transform', `translate(${margin.left}, ${margin.top})`);
    
    workflowLines.forEach((line, i) => {
      const lineGroup = legendGroup.append('g')
        .attr('transform', `translate(0, ${i * 25})`)
        .attr('class', 'legend-item')
        .on('click', () => {
          setSelectedLine(selectedLine === line.id ? null : line.id);
        });
      
      lineGroup.append('line')
        .attr('x1', 0)
        .attr('y1', 10)
        .attr('x2', 30)
        .attr('y2', 10)
        .attr('stroke', line.color)
        .attr('stroke-width', 4);
      
      lineGroup.append('text')
        .attr('x', 40)
        .attr('y', 14)
        .text(line.name);
    });

    // Initial reset zoom
    svg.call(zoomBehavior.transform, d3.zoomIdentity);

    // Add click handler to clear selection when clicking background
    svg.on('click', () => {
      setSelectedAgent(null);
      setSelectedCampaign(null);
    });

    // Apply any selections or filters
    applySelections();
    
    // Stop simulation after initial layout
    setTimeout(() => {
      if (!isSimulationRunning) {
        simulation.stop();
      }
    }, 2000);

    // Clean up function
    return () => {
      simulation.stop();
    };

  }, [nodesData, linksData, zoom.k, simulationParams, isSimulationRunning]); // Re-render on data or parameter changes

  // Apply highlighting based on selections
  useEffect(() => {
    applySelections();
  }, [selectedAgent, selectedCampaign, selectedLine, hoveredAgent]);

  // Function to apply selections and highlighting
  const applySelections = () => {
    if (!svgRef.current) return;
    
    const svg = d3.select(svgRef.current);
    
    // Reset all highlights and overlays
    svg.selectAll('.highlighted').classed('highlighted', false);
    svg.selectAll('.dimmed').classed('dimmed', false);
    svg.selectAll('.extreme-dimmed').classed('extreme-dimmed', false);
    
    // Add overlay backdrop if anything is selected
    const hasSelection = selectedAgent || selectedCampaign || selectedLine;
    
    // Add or remove the semi-transparent backdrop for focus
    const backdrop = svg.select('.focus-backdrop');
    if (hasSelection && backdrop.empty()) {
      // Create backdrop if it doesn't exist
      svg.insert('rect', '.main-group')
        .attr('class', 'focus-backdrop')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('fill', 'rgba(26, 26, 46, 0.7)')
        .style('opacity', 0)
        .transition()
        .duration(300)
        .style('opacity', 1);
    } else if (!hasSelection && !backdrop.empty()) {
      // Remove backdrop if no selection
      backdrop.transition()
        .duration(300)
        .style('opacity', 0)
        .remove();
    }
    
    // Apply extreme dimming to everything initially if there's a selection
    if (hasSelection) {
      svg.selectAll('.connection').classed('extreme-dimmed', true);
      svg.selectAll('.agent-station').classed('extreme-dimmed', true);
      svg.selectAll('.campaign').classed('extreme-dimmed', true);
    }
    
    // If a line is selected, highlight it and its stations
    if (selectedLine) {
      // Highlight selected line
      svg.selectAll(`.connection[data-line="${selectedLine}"]`)
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
      
      // Find and highlight stations on this line
      const lineConnections = connections.filter(c => c.lineId === selectedLine);
      const stationsOnLine = new Set();
      
      lineConnections.forEach(conn => {
        stationsOnLine.add(conn.source);
        stationsOnLine.add(conn.target);
      });
      
      stationsOnLine.forEach(stationId => {
        svg.select(`.agent-${stationId}`)
          .classed('highlighted', true)
          .classed('extreme-dimmed', false);
      });
      
      // Highlight campaigns on this line
      svg.selectAll('.campaign')
        .filter(function() {
          const campaignData = d3.select(this).datum();
          return campaignData && campaignData.lineId === selectedLine;
        })
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
    }
    
    // If an agent is selected, highlight it and its connections
    if (selectedAgent) {
      // Highlight the selected agent
      svg.select(`.agent-${selectedAgent.id}`)
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
      
      // Find all connections involving this agent
      svg.selectAll('.connection')
        .filter(function() {
          const source = d3.select(this).attr('data-source');
          const target = d3.select(this).attr('data-target');
          return source === selectedAgent.id || target === selectedAgent.id;
        })
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
      
      // Find agents connected to this agent
      const connectedAgents = connections
        .filter(c => c.source === selectedAgent.id || c.target === selectedAgent.id)
        .map(c => c.source === selectedAgent.id ? c.target : c.source);
      
      connectedAgents.forEach(agentId => {
        svg.select(`.agent-${agentId}`)
          .classed('highlighted', true)
          .classed('extreme-dimmed', false);
      });
      
      // Highlight campaigns currently at this agent
      svg.selectAll('.campaign')
        .filter(function() {
          const campaignData = d3.select(this).datum();
          return campaignData && campaignData.currentStationId === selectedAgent.id;
        })
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
    }
    
    // If a campaign is selected, highlight it and its path
    if (selectedCampaign) {
      svg.select(`.campaign-${selectedCampaign.id}`)
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
      
      // Highlight current and next station
      svg.select(`.agent-${selectedCampaign.currentStationId}`)
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
        
      if (selectedCampaign.nextStationId) {
        svg.select(`.agent-${selectedCampaign.nextStationId}`)
          .classed('highlighted', true)
          .classed('extreme-dimmed', false);
      }
      
      // Highlight the connection between current and next station
      svg.selectAll('.connection')
        .filter(function() {
          const source = d3.select(this).attr('data-source');
          const target = d3.select(this).attr('data-target');
          const line = d3.select(this).attr('data-line');
          return source === selectedCampaign.currentStationId && 
                 target === selectedCampaign.nextStationId &&
                 line === selectedCampaign.lineId;
        })
        .classed('highlighted', true)
        .classed('extreme-dimmed', false);
      
      // Highlight all connections of the campaign's line type 
      // to show the full route possibilities
      svg.selectAll(`.connection[data-line="${selectedCampaign.lineId}"]`)
        .classed('dimmed', true)
        .classed('extreme-dimmed', false);
      
      // Highlight previous stations and connections in journey
      if (selectedCampaign.previousStations && selectedCampaign.previousStations.length > 0) {
        selectedCampaign.previousStations.forEach((station, index) => {
          svg.select(`.agent-${station.stationId}`)
            .classed('highlighted', true)
            .classed('extreme-dimmed', false);
          
          // Highlight connection to next station in journey
          if (index < selectedCampaign.previousStations.length - 1) {
            const nextStation = selectedCampaign.previousStations[index + 1];
            svg.selectAll('.connection')
              .filter(function() {
                const source = d3.select(this).attr('data-source');
                const target = d3.select(this).attr('data-target');
                const line = d3.select(this).attr('data-line');
                return ((source === station.stationId && target === nextStation.stationId) ||
                       (source === nextStation.stationId && target === station.stationId)) &&
                       line === selectedCampaign.lineId;
              })
              .classed('highlighted', true)
              .classed('extreme-dimmed', false);
          }
        });
        
        // Highlight connection from last previous station to current station
        const lastPrevStation = selectedCampaign.previousStations[selectedCampaign.previousStations.length - 1];
        svg.selectAll('.connection')
          .filter(function() {
            const source = d3.select(this).attr('data-source');
            const target = d3.select(this).attr('data-target');
            const line = d3.select(this).attr('data-line');
            return ((source === lastPrevStation.stationId && target === selectedCampaign.currentStationId) ||
                   (source === selectedCampaign.currentStationId && target === lastPrevStation.stationId)) &&
                   line === selectedCampaign.lineId;
          })
          .classed('highlighted', true)
          .classed('extreme-dimmed', false);
      }
    }
    
    // If an agent is hovered, highlight it
    if (hoveredAgent) {
      svg.select(`.agent-${hoveredAgent.id}`).classed('hovered', true);
    } else {
      svg.selectAll('.hovered').classed('hovered', false);
    }
    
    // Enhance the highlighted elements
    svg.selectAll('.highlighted')
      .style('transform', 'scale(1.05)')
      .style('transition', 'transform 0.3s ease');
  };

  // Handler for zooming in
  const handleZoomIn = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const zoomBehavior = d3.zoom().on('zoom', (event) => {
      setZoom(event.transform);
      svg.select('.main-group').attr('transform', event.transform);
    });
    
    svg.transition().call(
      zoomBehavior.scaleBy, 1.3
    );
  };

  // Handler for zooming out
  const handleZoomOut = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const zoomBehavior = d3.zoom().on('zoom', (event) => {
      setZoom(event.transform);
      svg.select('.main-group').attr('transform', event.transform);
    });
    
    svg.transition().call(
      zoomBehavior.scaleBy, 0.7
    );
  };

  // Handler for resetting zoom
  const handleResetZoom = () => {
    if (!svgRef.current) return;
    const svg = d3.select(svgRef.current);
    const zoomBehavior = d3.zoom().on('zoom', (event) => {
      setZoom(event.transform);
      svg.select('.main-group').attr('transform', event.transform);
    });
    
    svg.transition().call(
      zoomBehavior.transform, d3.zoomIdentity
    );
  };
  
  // Handler for toggling simulation
  const handleToggleSimulation = () => {
    setIsSimulationRunning(!isSimulationRunning);
    if (!simulationRef.current) return;
    
    if (!isSimulationRunning) {
      // Resume simulation
      simulationRef.current.alpha(0.3).restart();
      
      // Release fixed positions
      nodesData.forEach(node => {
        node.fx = null;
        node.fy = null;
      });
    } else {
      // Stop simulation and fix all nodes in place
      simulationRef.current.stop();
      
      // Fix nodes in current positions
      nodesData.forEach(node => {
        node.fx = node.x;
        node.fy = node.y;
      });
    }
  };
  
  // Handler for adjusting simulation parameters
  const handleAdjustSimulation = (param, value) => {
    setSimulationParams(prev => {
      const newParams = { ...prev, [param]: value };
      
      // Update simulation with new parameters if it exists
      if (simulationRef.current) {
        switch(param) {
          case 'forceStrength':
            simulationRef.current.force('link').strength(value);
            break;
          case 'linkDistance':
            simulationRef.current.force('link').distance(value);
            break;
          case 'chargeStrength':
            simulationRef.current.force('charge').strength(value);
            break;
          case 'collisionRadius':
            simulationRef.current.force('collision').radius(value);
            break;
          case 'centerForceX':
            simulationRef.current.force('x').strength(value);
            break;
          case 'centerForceY':
            simulationRef.current.force('y').strength(value);
            break;
          default:
            // For parameters that need simulation restart
            simulationRef.current.alpha(newParams.alpha)
              .alphaDecay(newParams.alphaDecay)
              .alphaMin(newParams.alphaMin)
              .velocityDecay(newParams.velocityDecay)
              .restart();
        }
      }
      
      return newParams;
    });
  };
  
  // Handler for re-running the simulation
  const handleRestartSimulation = () => {
    if (!simulationRef.current) return;
    simulationRef.current.alpha(simulationParams.alpha).restart();
  };

  // Toggle simulation parameters panel
  const [showSimulationParams, setShowSimulationParams] = useState(false);
  
  return (
    <div className="subway-map-container">
      <div className="subway-controls">
        <div className="control-group">
          <h4>View Controls</h4>
          <button onClick={handleZoomIn} title="Zoom In">+</button>
          <button onClick={handleZoomOut} title="Zoom Out">-</button>
          <button onClick={handleResetZoom} title="Reset Zoom">Reset</button>
        </div>
        
        <div className="control-group">
          <h4>Layout Controls</h4>
          <button 
            onClick={handleToggleSimulation} 
            className={isSimulationRunning ? 'active' : ''}
            title={isSimulationRunning ? 'Pause Simulation' : 'Resume Simulation'}
          >
            {isSimulationRunning ? '⏸' : '▶️'}
          </button>
          <button onClick={handleRestartSimulation} title="Restart Simulation">🔄</button>
          <button 
            onClick={() => setShowSimulationParams(!showSimulationParams)}
            className={showSimulationParams ? 'active' : ''}
            title="Simulation Parameters"
          >
            ⚙️
          </button>
        </div>
      </div>
      
      {/* Simulation Parameters Panel */}
      <div className={`simulation-parameters ${showSimulationParams ? 'visible' : ''}`}>
        <h4>Simulation Parameters</h4>
        
        <div className="parameter-group">
          <label className="parameter-label">
            Link Distance
            <span className="parameter-value">{simulationParams.linkDistance}</span>
          </label>
          <input 
            type="range" 
            min="30" 
            max="200" 
            value={simulationParams.linkDistance}
            onChange={(e) => handleAdjustSimulation('linkDistance', Number(e.target.value))}
          />
        </div>
        
        <div className="parameter-group">
          <label className="parameter-label">
            Charge Strength
            <span className="parameter-value">{simulationParams.chargeStrength}</span>
          </label>
          <input 
            type="range" 
            min="-1000" 
            max="-100" 
            value={simulationParams.chargeStrength}
            onChange={(e) => handleAdjustSimulation('chargeStrength', Number(e.target.value))}
          />
        </div>
        
        <div className="parameter-group">
          <label className="parameter-label">
            Force Strength
            <span className="parameter-value">{simulationParams.forceStrength.toFixed(2)}</span>
          </label>
          <input 
            type="range" 
            min="0.1" 
            max="1" 
            step="0.1"
            value={simulationParams.forceStrength}
            onChange={(e) => handleAdjustSimulation('forceStrength', Number(e.target.value))}
          />
        </div>
        
        <div className="parameter-group">
          <label className="parameter-label">
            Collision Radius
            <span className="parameter-value">{simulationParams.collisionRadius}</span>
          </label>
          <input 
            type="range" 
            min="10" 
            max="60" 
            value={simulationParams.collisionRadius}
            onChange={(e) => handleAdjustSimulation('collisionRadius', Number(e.target.value))}
          />
        </div>
        
        <div className="parameter-group">
          <label className="parameter-label">
            Center Force
            <span className="parameter-value">{simulationParams.centerForceX.toFixed(2)}</span>
          </label>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.1"
            value={simulationParams.centerForceX}
            onChange={(e) => {
              const value = Number(e.target.value);
              handleAdjustSimulation('centerForceX', value);
              handleAdjustSimulation('centerForceY', value);
            }}
          />
        </div>
        
        <button 
          className="toggle-button"
          onClick={handleRestartSimulation}
        >
          Apply Changes
        </button>
      </div>
      <svg 
        ref={svgRef} 
        className="subway-map"
        width="100%" 
        height="800px"
      ></svg>
      
      {/* Details Panel */}
      <div className={`details-panel ${(selectedAgent || selectedCampaign) ? 'visible' : ''}`}>
        {selectedAgent && (
          <div className="agent-details">
            <h3>{selectedAgent.name}</h3>
            <p className="role">{selectedAgent.role}</p>
            <p className="office">Office: {selectedAgent.office}</p>
            <p className="description">{selectedAgent.description}</p>
            <button onClick={() => setSelectedAgent(null)}>Close</button>
          </div>
        )}
        
        {selectedCampaign && (
          <div className="campaign-details">
            <h3>{selectedCampaign.name}</h3>
            <div className="campaign-meta">
              <span className="type">Type: {selectedCampaign.type}</span>
              <span className="priority">Priority: {selectedCampaign.priority}</span>
              <span className={`status status-${selectedCampaign.status}`}>
                Status: {selectedCampaign.status}
              </span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${selectedCampaign.progress}%`, backgroundColor: getStatusColor(selectedCampaign.status) }}
              ></div>
            </div>
            <p className="progress-text">{selectedCampaign.progress}% Complete</p>
            <p className="current-stage">
              <strong>Current Stage:</strong> {agents.find(a => a.id === selectedCampaign.currentStationId)?.name || 'Unknown'}
            </p>
            <p className="next-stage">
              <strong>Next Stage:</strong> {agents.find(a => a.id === selectedCampaign.nextStationId)?.name || 'Final Stage'}
            </p>
            <p className="timeline">
              <strong>Started:</strong> {new Date(selectedCampaign.startedAt).toLocaleDateString()}
              <br />
              <strong>Estimated Completion:</strong> {new Date(selectedCampaign.estimatedCompletion).toLocaleDateString()}
            </p>
            <h4>Journey Timeline</h4>
            <div className="journey-timeline">
              {selectedCampaign.previousStations.map((station, index) => (
                <div key={index} className="journey-item completed">
                  <div className="journey-point"></div>
                  <div className="journey-content">
                    <strong>{agents.find(a => a.id === station.stationId)?.name || 'Unknown'}</strong>
                    <small>
                      {new Date(station.enteredAt).toLocaleDateString()} - 
                      {new Date(station.exitedAt).toLocaleDateString()}
                    </small>
                  </div>
                </div>
              ))}
              <div className="journey-item current">
                <div className="journey-point"></div>
                <div className="journey-content">
                  <strong>{agents.find(a => a.id === selectedCampaign.currentStationId)?.name || 'Unknown'}</strong>
                  <small>Current Stage</small>
                </div>
              </div>
              <div className="journey-item future">
                <div className="journey-point"></div>
                <div className="journey-content">
                  <strong>{agents.find(a => a.id === selectedCampaign.nextStationId)?.name || 'Unknown'}</strong>
                  <small>Next Stage</small>
                </div>
              </div>
            </div>
            <button onClick={() => setSelectedCampaign(null)}>Close Details</button>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to get color based on campaign status
const getStatusColor = (status) => {
  switch (status) {
    case 'on-time': return '#4caf50'; // Green
    case 'delayed': return '#f44336'; // Red
    case 'expedited': return '#2196f3'; // Blue
    case 'paused': return '#ff9800'; // Orange
    default: return '#757575'; // Grey
  }
};

export default SubwayMap;