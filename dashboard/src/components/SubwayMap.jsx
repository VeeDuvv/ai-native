// SPDX-License-Identifier: MIT
// Copyright (c) 2025 Vamsi Duvvuri

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { agents, workflowLines, connections, activeCampaigns } from '../data/workflows';
import './SubwayMap.css';

const SubwayMap = () => {
  const svgRef = useRef(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedCampaign, setSelectedCampaign] = useState(null);
  const [selectedLine, setSelectedLine] = useState(null);
  const [hoveredAgent, setHoveredAgent] = useState(null);
  const [zoom, setZoom] = useState({ k: 1, x: 0, y: 0 });

  // Initialize and render the subway map
  useEffect(() => {
    if (!svgRef.current) return;

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

    // Draw connections (subway lines)
    connections.forEach(connection => {
      const line = workflowLines.find(l => l.id === connection.lineId);
      const source = agents.find(a => a.id === connection.source);
      const target = agents.find(a => a.id === connection.target);
      
      if (!source || !target || !line) return;
      
      // Create a path generator for curved lines
      const midX = (source.position.x + target.position.x) / 2;
      const midY = (source.position.y + target.position.y) / 2 - 20; // Curve upward slightly
      
      const path = `M${source.position.x},${source.position.y} 
                    Q${midX},${midY} 
                    ${target.position.x},${target.position.y}`;
      
      connectionsGroup.append('path')
        .attr('d', path)
        .attr('stroke', line.color)
        .attr('stroke-width', 4)
        .attr('fill', 'none')
        .attr('class', `connection connection-${connection.id} line-${line.id}`)
        .attr('data-source', source.id)
        .attr('data-target', target.id)
        .attr('data-line', line.id);
    });

    // Draw agents (stations)
    agentsGroup.selectAll('.agent-station')
      .data(agents)
      .enter()
      .append('g')
      .attr('class', d => `agent-station agent-${d.id} office-${d.office}`)
      .attr('transform', d => `translate(${d.position.x}, ${d.position.y})`)
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
          
        // Add label
        labelsGroup.append('text')
          .attr('x', d.position.x)
          .attr('y', d.position.y + 25)
          .attr('text-anchor', 'middle')
          .attr('class', 'agent-label')
          .text(d.name);
      });

    // Draw active campaigns (trains)
    activeCampaigns.forEach(campaign => {
      const line = workflowLines.find(l => l.id === campaign.lineId);
      const currentStation = agents.find(a => a.id === campaign.currentStationId);
      
      if (!currentStation || !line) return;
      
      // Find the connection to the next station
      const nextConnection = connections.find(c => 
        c.source === campaign.currentStationId && 
        c.target === campaign.nextStationId &&
        c.lineId === campaign.lineId
      );
      
      if (!nextConnection) return;
      
      const nextStation = agents.find(a => a.id === campaign.nextStationId);
      
      // Calculate position along the connection (based on progress)
      const progress = campaign.progress / 100;
      const campaignX = currentStation.position.x + (nextStation.position.x - currentStation.position.x) * progress;
      const campaignY = currentStation.position.y + (nextStation.position.y - currentStation.position.y) * progress;
      
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

  }, [zoom.k]); // Re-render on zoom changes

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

  return (
    <div className="subway-map-container">
      <div className="subway-controls">
        <button onClick={handleZoomIn}>+</button>
        <button onClick={handleZoomOut}>-</button>
        <button onClick={handleResetZoom}>Reset</button>
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