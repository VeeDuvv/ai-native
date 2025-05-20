# AI-Native Ad Agency

> Building the future of advertising with AI-first principles

## Overview

This repository contains the architecture, design, and implementation of an AI-native advertising agency platform. We're creating a system where autonomous AI agents collaborate to plan, create, and optimize advertising campaigns with minimal human intervention.

## Vision

Our vision is to revolutionize the advertising industry by building a truly AI-native platform that leverages the power of autonomous agents while maintaining the flexibility to adapt to changing requirements and technologies.

## Core Principles

- **Agent-First Architecture**: Autonomous AI agents as first-class citizens
- **API-First Design**: All functionality built as APIs first, interfaces second
- **Extensibility Over Optimization**: Prioritizing the ability to extend our system
- **Separation of Concerns**: Clean separation between system components
- **Data-Driven Evolution**: System learns and improves based on its own operation
- **Minimizing Technical Debt**: Long-term focus over short-term gains
- **Human-AI Collaboration**: Designing for effective collaboration

## Repository Structure

- `docs/`: Documentation for architecture, planning, and processes
  - `architecture/`: System architecture and component design
  - `planning/`: Development roadmap and planning documents
- `src/`: Source code for the platform
  - `agent_framework/`: Core agent framework implementation
    - `communication/`: Agent communication protocols and examples
    - `core/`: Base agent classes and interfaces
    - `metrics/`: Observability and metrics collection
  - `api_layer/`: API layer implementation
  - `tisit/`: This Is What It Is - Knowledge graph system
    - Entity-based knowledge representation
    - Relationship modeling
    - Knowledge storage and retrieval
    - Agent integration interfaces

## Current Status

This project is in active development. We have implemented:

1. Core agent framework architecture
2. Specialized agent types (Strategy, Creative, Media, Analytics, Client Communication)
3. Client-facing dashboard
4. Campaign analytics system
5. TISIT knowledge graph for collective intelligence
   - Entity-based knowledge representation
   - Knowledge graph with relationship modeling
   - REST API for programmatic access
   - Interactive knowledge graph visualization dashboard
6. Security and compliance features

## Running the TISIT Knowledge Graph

### Start the API Server

```bash
# Start the TISIT API server
python -m src.tisit.api_server --host localhost --port 8000
```

### Start the Dashboard

```bash
# Install dependencies
npm install

# Start the dashboard development server
npm run start:dashboard
```

Then open your browser to http://localhost:3000 to access the knowledge graph dashboard.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- Vamsi Duvvuri - Project Lead

---

© 2025 Vamsi Duvvuri