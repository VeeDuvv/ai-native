# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Max Optimizer (Campaign Manager) Workflow

## Agent Overview

Max Optimizer serves as the Campaign Manager in Koya's middle office, responsible for implementing, monitoring, and optimizing advertising campaigns across various channels. Max works closely with James Planner, Zara Buyer, and Lucas Director to ensure campaigns are executed according to plan, while continuously optimizing performance to meet or exceed KPIs.

## Workflow Stages

### Stage 1: Campaign Setup & Implementation

**Inputs:**
- Campaign brief and strategy (from Carlos Planner)
- Creative assets and guidelines (from Lucas Director)
- Media plan with channels, budget, and timeline (from James Planner)
- Media buying details and placements (from Zara Buyer)

**Memory Activation:**
- *Working Memory:* Campaign brief, creative assets, media plan, buying details
- *Long-term Memory:* Historical campaign performance, platform-specific implementation requirements, technical specifications for each channel

**Action Space:**
- *Internal Actions:*
  - Review all campaign materials for completeness
  - Create implementation checklist for each channel
  - Set up tracking parameters and attribution models
  - Configure campaign dashboards and alerts
- *External Actions:*
  - Set up campaigns in ad platforms (Google, Meta, TikTok, etc.)
  - Upload creative assets to respective platforms
  - Configure targeting parameters based on media plan
  - Implement tracking codes across all digital touchpoints

**Decision Procedures:**
- *Goal:* Successfully implement campaign across all channels with proper tracking
- *Planning:* Create sequential implementation schedule based on launch timeline
- *Execution:* Configure all campaign elements in platform interfaces
- *Evaluation:* Verify all campaigns are set up correctly with A/B testing framework where applicable

**Outputs:**
- Campaign implementation status report (to Carlos Planner)
- Creative asset deployment confirmation (to Lucas Director)
- Media activation confirmation (to James Planner)
- Platform-specific implementation details (to Maya Analyzer for tracking)

### Stage 2: Campaign Monitoring & Data Collection

**Inputs:**
- Live campaign data streams from all platforms
- Website and conversion tracking data
- Attribution model parameters

**Memory Activation:**
- *Working Memory:* Real-time performance metrics, platform notifications, tracking issues
- *Long-term Memory:* Expected performance benchmarks, typical performance patterns, previous campaign issues and solutions

**Action Space:**
- *Internal Actions:*
  - Aggregate data from multiple platforms into unified dashboard
  - Calculate cross-platform KPIs and attribution
  - Identify early performance trends or anomalies
  - Track creative performance across placements
- *External Actions:*
  - Pull reports from ad platforms via APIs
  - Monitor delivery pacing and impression share
  - Check for disapproved ads or policy issues
  - Verify tracking integrity across touchpoints

**Decision Procedures:**
- *Goal:* Maintain comprehensive visibility on campaign performance
- *Planning:* Establish monitoring schedule (hourly, daily, weekly) by KPI importance
- *Execution:* Systematically collect and process data from all sources
- *Evaluation:* Assess data quality and completeness, flag inconsistencies

**Outputs:**
- Real-time performance dashboards (to Carlos Planner and Maya Analyzer)
- Data quality and tracking status reports (to Ben Engineer)
- Early performance indicators (to James Planner and Zara Buyer)
- Creative performance metrics (to Lucas Director)

### Stage 3: Performance Analysis & Optimization

**Inputs:**
- Aggregated campaign performance data
- Performance benchmarks and KPI targets
- Budget utilization and pacing data
- Competitive intelligence (from Maya Analyzer)

**Memory Activation:**
- *Working Memory:* Current performance metrics, optimization opportunities, budget allocation
- *Long-term Memory:* Optimization tactics that worked for similar campaigns, performance patterns by channel, audience response to similar messaging

**Action Space:**
- *Internal Actions:*
  - Analyze performance against KPIs by channel, creative, audience
  - Identify underperforming and overperforming segments
  - Calculate efficiency metrics (CPA, ROAS, CPM)
  - Model budget reallocation scenarios
- *External Actions:*
  - Adjust bids and budgets across platforms
  - Pause underperforming ads and scale winners
  - Refine audience targeting based on performance
  - A/B test new creative variations or messaging
  - Implement dayparting or geographic optimizations

**Decision Procedures:**
- *Goal:* Maximize campaign performance against primary KPIs
- *Planning:* Prioritize optimization actions by potential impact
- *Execution:* Implement changes methodically with control groups where possible
- *Evaluation:* Measure lift from each optimization action

**Outputs:**
- Optimization recommendations and actions taken (to Carlos Planner)
- Budget reallocation suggestions (to James Planner and Zara Buyer)
- Creative performance insights and recommendations (to Lucas Director)
- Audience targeting refinements (to Olivia Researcher)

### Stage 4: Reporting & Insights Development

**Inputs:**
- Complete campaign performance dataset
- Original campaign objectives and KPIs
- Optimization history and impact analysis
- Client reporting requirements

**Memory Activation:**
- *Working Memory:* Key performance highlights, variances from plan, optimization results
- *Long-term Memory:* Previous reporting frameworks, client preferences, industry benchmarks, historical campaign comparisons

**Action Space:**
- *Internal Actions:*
  - Synthesize campaign data into coherent narrative
  - Identify key learnings and insights
  - Calculate ROI and efficiency metrics
  - Prepare data visualizations and executive summaries
- *External Actions:*
  - Generate automated reports from platforms
  - Export custom reports for client presentation
  - Document optimization decisions and results
  - Archive campaign data for future reference

**Decision Procedures:**
- *Goal:* Translate complex campaign data into actionable insights
- *Planning:* Structure reporting by KPIs, channels, and audience segments
- *Execution:* Create comprehensive yet accessible reporting
- *Evaluation:* Ensure reports answer key business questions and provide strategic value

**Outputs:**
- Comprehensive campaign performance report (to Carlos Planner)
- Channel-specific performance analysis (to James Planner)
- Creative performance evaluation (to Lucas Director)
- Media efficiency analysis (to Zara Buyer)
- Strategic insights and recommendations for future campaigns (to Maya Analyzer and Simon Strategist)
- Performance data for client dashboards (to Front Office agents)

## CoALA Implementation

### Memory Systems
Max Optimizer utilizes a sophisticated memory architecture combining:

1. **Structured Campaign Data Store (Long-term):**
   - SQL database storing historical campaign configurations, performance metrics, and optimization actions
   - Queryable by client, campaign type, channel, timing, and KPIs

2. **Real-time Performance Cache (Working):**
   - In-memory data store for current campaign metrics and alerts
   - Refreshes automatically on configurable intervals by channel

3. **Optimization Knowledge Base (Long-term):**
   - Vector database of optimization tactics, their contexts, and measured impacts
   - Supports similarity search to find relevant optimization approaches

4. **Platform Configuration Memory (Long-term):**
   - Structured database of implementation requirements for each ad platform
   - Includes templates, specifications, and best practices

### Action Space
Max's action space spans both analytical and operational domains:

1. **Analytics Interface:**
   - Data aggregation and unification across platforms
   - Statistical analysis for performance evaluation
   - Anomaly detection and alert generation
   - Predictive modeling for optimization opportunities

2. **Platform Management Interface:**
   - API connections to all major ad platforms
   - Automated implementation and adjustment capabilities
   - Creative asset management and deployment
   - Targeting and budget adjustment functions

3. **Reporting Engine:**
   - Automated data visualization tools
   - Narrative generation for performance storytelling
   - Custom reporting templates by client and campaign type
   - Interactive dashboards for real-time monitoring

### Decision Procedures
Max employs a systematic approach to campaign management decisions:

1. **Implementation Protocol:**
   - Checklist-based verification for campaign setup
   - Technical QA procedures for each platform
   - Tracking validation process

2. **Monitoring Framework:**
   - Tiered alert system based on KPI variance thresholds
   - Automated diagnostic procedures for performance issues
   - Cross-platform performance correlation analysis

3. **Optimization Algorithm:**
   - Statistical significance testing for performance variations
   - Multi-armed bandit approach for creative and audience optimization
   - Budget allocation optimizer based on efficiency metrics
   - Marginal return analysis for investment decisions

4. **Insight Derivation Process:**
   - Pattern recognition across campaign dimensions
   - Comparative analysis against benchmarks and historical performance
   - Causal analysis linking optimization actions to outcomes
   - Forward-looking recommendation framework