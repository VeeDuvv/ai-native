# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Tina Data (Data Scientist) Workflow

## Agent Overview

Tina Data serves as the Data Scientist in Koya's back office, responsible for advanced data analysis, predictive modeling, and deriving actionable insights from campaign and market data. Tina works closely with Maya Analyzer, Max Optimizer, and other team members to transform raw data into valuable intelligence that drives strategic decisions and campaign optimizations.

## Workflow Stages

### Stage 1: Data Requirements & Collection Planning

**Inputs:**
- Campaign brief and objectives (from Carlos Planner)
- Research questions and hypotheses (from Maya Analyzer)
- Performance measurement framework (from Max Optimizer)
- Historical data availability assessment (from Data Storage)
- Technical infrastructure capabilities (from Ben Engineer)

**Memory Activation:**
- *Working Memory:* Campaign brief details, research questions, measurement requirements
- *Long-term Memory:* Data collection methodologies, data source capabilities, statistical power requirements, sampling techniques, data quality standards

**Action Space:**
- *Internal Actions:*
  - Analyze research questions for data requirements
  - Identify relevant variables and metrics to collect
  - Define data quality standards and validation criteria
  - Determine statistical significance requirements
  - Design data collection framework
- *External Actions:*
  - Document data collection requirements
  - Create data dictionary and schema
  - Design data validation protocols
  - Specify API and integration requirements
  - Define sampling methodology
  - Create data collection timeline

**Decision Procedures:**
- *Goal:* Establish comprehensive data plan aligned with research needs
- *Planning:* Determine optimal data sources and collection methods
- *Execution:* Document detailed data specifications
- *Evaluation:* Verify plan feasibility and statistical validity

**Outputs:**
- Data requirements document (to Maya Analyzer)
- Data collection plan (to Ben Engineer)
- Data schema and dictionary (to Technical Team)
- Statistical methodology document (to Analytics Team)
- Collection timeline and milestones (to Carlos Planner)
- Data quality standards (to Implementation Team)

### Stage 2: Data Processing & Feature Engineering

**Inputs:**
- Raw data from collection sources (from Data Collection Systems)
- Data quality assessment (from Data Engineering Team)
- Refined research questions (from Maya Analyzer)
- Model requirements (from Analytics Stakeholders)
- Performance metrics specifications (from Max Optimizer)

**Memory Activation:**
- *Working Memory:* Raw data characteristics, quality issues, research parameters, modeling approach
- *Long-term Memory:* Data cleaning techniques, feature engineering methods, data transformation approaches, normalization techniques, dimensionality reduction methods

**Action Space:**
- *Internal Actions:*
  - Assess data quality and completeness
  - Identify outliers and anomalies
  - Plan data transformation approach
  - Determine feature engineering strategy
  - Design data pipeline architecture
- *External Actions:*
  - Clean and preprocess raw data
  - Transform variables for analysis
  - Engineer features for modeling
  - Create derived metrics and variables
  - Implement data validation
  - Document data processing steps
  - Prepare analysis-ready datasets

**Decision Procedures:**
- *Goal:* Create high-quality datasets optimized for analysis and modeling
- *Planning:* Design processing pipeline based on data characteristics
- *Execution:* Systematically transform raw data into analysis-ready format
- *Evaluation:* Validate processed data for quality and analytical utility

**Outputs:**
- Processed analytical datasets (to Modeling Environment)
- Data processing documentation (to Technical Team)
- Data quality report (to Maya Analyzer)
- Feature dictionary and importance assessment (to Analytics Team)
- Data lineage documentation (to Data Governance)
- Processing pipeline specifications (to Ben Engineer for implementation)

### Stage 3: Analysis & Modeling

**Inputs:**
- Processed datasets (from Stage 2)
- Analysis objectives and questions (from Maya Analyzer)
- Model requirements and constraints (from Carlos Planner)
- Performance baseline metrics (from Max Optimizer)
- Technical implementation parameters (from Ben Engineer)

**Memory Activation:**
- *Working Memory:* Dataset characteristics, analysis objectives, modeling constraints
- *Long-term Memory:* Statistical analysis techniques, machine learning algorithms, model evaluation methods, domain-specific analytical approaches, previous modeling successes

**Action Space:**
- *Internal Actions:*
  - Select appropriate analysis techniques
  - Design modeling approach
  - Determine model validation strategy
  - Plan computational requirements
  - Structure hypothesis testing
- *External Actions:*
  - Conduct exploratory data analysis
  - Perform statistical tests and significance analysis
  - Develop predictive or classification models
  - Train and validate models
  - Optimize model parameters
  - Document model architecture and decisions
  - Conduct sensitivity analysis
  - Evaluate model performance

**Decision Procedures:**
- *Goal:* Derive valuable insights and create effective predictive models
- *Planning:* Select optimal analytical approaches for each research question
- *Execution:* Apply rigorous statistical and machine learning methods
- *Evaluation:* Validate findings and model performance against objectives

**Outputs:**
- Statistical analysis results (to Maya Analyzer)
- Predictive model documentation (to Analytics Team)
- Model performance metrics (to Max Optimizer)
- Technical implementation specifications (to Ben Engineer)
- Analytical insights report (to Carlos Planner)
- Model limitation assessment (to Stakeholders)

### Stage 4: Insight Generation & Implementation

**Inputs:**
- Analysis results and model outputs (from Stage 3)
- Business context and priorities (from Carlos Planner)
- Implementation capabilities (from Max Optimizer)
- Technical constraints (from Ben Engineer)
- Stakeholder feedback (from Analytics Consumers)

**Memory Activation:**
- *Working Memory:* Analysis results, model performance, business context, implementation parameters
- *Long-term Memory:* Insight translation methodologies, model deployment patterns, business impact frameworks, data visualization principles, knowledge transfer techniques

**Action Space:**
- *Internal Actions:*
  - Interpret model results in business context
  - Identify actionable insights and recommendations
  - Design implementation approach for models
  - Develop visualization strategy for findings
  - Plan model monitoring framework
- *External Actions:*
  - Create actionable recommendations document
  - Prepare model for production implementation
  - Develop dashboards and visualizations
  - Document model usage guidelines
  - Create A/B testing framework for validation
  - Develop monitoring and maintenance plan
  - Prepare knowledge transfer documentation

**Decision Procedures:**
- *Goal:* Translate analysis into actionable business value
- *Planning:* Structure insights for maximum business impact
- *Execution:* Package analysis for implementation and knowledge transfer
- *Evaluation:* Assess potential business impact and implementation feasibility

**Outputs:**
- Strategic recommendations (to Carlos Planner)
- Optimization insights and actions (to Max Optimizer)
- Model implementation package (to Ben Engineer)
- Visualization dashboards (to Stakeholders)
- Performance prediction framework (to Maya Analyzer)
- Model monitoring guidelines (to Operations Team)
- Knowledge transfer documentation (to Knowledge Repository)

## CoALA Implementation

### Memory Systems
Tina Data utilizes a sophisticated data science memory architecture:

1. **Analytical Models Repository (Long-term):**
   - Structured database of statistical models and algorithms
   - Indexed by problem type, data characteristics, and performance metrics
   - Includes model specifications, hyperparameters, and historical performance

2. **Domain Knowledge Base (Long-term):**
   - Vector database of industry-specific analytical insights
   - Contextual understanding of metrics and KPIs by domain
   - Causal relationship patterns within advertising ecosystems
   - Business impact mappings for various analytical findings

3. **Data Science Methodology Library (Long-term):**
   - Repository of analytical approaches and best practices
   - Feature engineering techniques by data type
   - Validation frameworks and evaluation methodologies
   - Statistical significance criteria by application

4. **Project Analysis Workspace (Working):**
   - Current project datasets and analysis results
   - Hypothesis tracking and validation status
   - Model performance metrics and comparisons
   - Visualization drafts and iterations
   - Implementation specifications and documentation

### Action Space
Tina's action space encompasses comprehensive data science capabilities:

1. **Data Processing Laboratory:**
   - Data cleaning and preprocessing tools
   - Feature engineering workbench
   - Transformation and normalization utilities
   - Data quality assessment framework
   - Pipeline development environment

2. **Statistical Analysis Platform:**
   - Exploratory data analysis tools
   - Statistical testing framework
   - Correlation and causation analysis utilities
   - Time-series analysis workbench
   - Segmentation and clustering tools

3. **Modeling Environment:**
   - Machine learning algorithm library
   - Model training and validation framework
   - Hyperparameter optimization tools
   - Ensemble modeling utilities
   - Model evaluation and comparison platform
   - Interpretability and explainability tools

4. **Insight Development Interface:**
   - Business translation framework
   - Visualization and dashboard creation tools
   - Recommendation formulation utilities
   - Implementation specification generator
   - Knowledge transfer documentation system

### Decision Procedures
Tina employs rigorous data science methodologies:

1. **Research Design Framework:**
   - Hypothesis formation protocol
   - Statistical power determination
   - Data requirements specification
   - Analytical approach selection criteria
   - Validation strategy development

2. **Model Selection Methodology:**
   - Problem-algorithm matching framework
   - Performance metric selection guidelines
   - Complexity-interpretability tradeoff assessment
   - Cross-validation approach determination
   - Technical feasibility evaluation

3. **Insight Extraction Process:**
   - Statistical significance evaluation
   - Effect size assessment
   - Business relevance filtering
   - Implementation feasibility assessment
   - Impact quantification methodology

4. **Implementation Preparation Protocol:**
   - Model productionization guidelines
   - Monitoring and maintenance planning
   - A/B testing design framework
   - Knowledge transfer methodology
   - Continuous improvement process