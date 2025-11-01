# ISO 14040:2006 & ISO 14044:2006 Integration Plan

## Executive Summary

This plan outlines the integration of ISO 14040:2006 (Principles and Framework) and ISO 14044:2006 (Requirements and Guidelines) into the LCA application. The integration covers both fixing existing features and adding new ISO-compliant capabilities.

**Estimated Effort**: 175-225 hours (~5-6 weeks full-time)
**Approach**: Phased implementation with testing between each phase

---

## Phase 1: Critical Compliance & Data Foundation

**Priority**: IMMEDIATE
**Estimated Effort**: 40-50 hours

### 1.1 Goal and Scope Definition System

**ISO Requirement**: ISO 14044:2006, Section 4.2.3 - Goal and scope shall be clearly defined and consistent with intended application

**Current Gap**: No system for documenting study goals, system boundaries, functional units, or assumptions

**Implementation**:

#### Backend Changes (`backend/services/openlca_service.py`)
- Add new data structures for Goal & Scope:
  ```python
  @dataclass
  class GoalAndScope:
      study_goal: str
      intended_application: str
      reasons_for_study: str
      intended_audience: str
      functional_unit: FunctionalUnit
      system_boundary: SystemBoundary
      data_quality_requirements: DataQuality
      assumptions: List[str]
      limitations: List[str]
      allocation_rules: List[str]

  @dataclass
  class FunctionalUnit:
      description: str  # e.g., "Production of 1 kg of glass fiber composite"
      quantified_performance: str  # What function does the product provide?
      reference_flow: str  # The flow that delivers this function
      amount: float
      unit: str
  ```

- New methods in `OpenLCAService`:
  - `save_goal_and_scope(goal_scope: GoalAndScope) -> str`
  - `get_goal_and_scope(study_id: str) -> GoalAndScope`
  - Store in JSON files in `backend/studies/` directory

#### Backend API Changes (`backend/app.py`)
- New endpoints:
  - `POST /api/goal-scope` - Create/update goal and scope
  - `GET /api/goal-scope/{study_id}` - Retrieve goal and scope
  - Update `/api/calculate` to require or accept `study_id` parameter

#### Frontend Changes
- New component: `frontend/src/components/GoalScopeForm.jsx`
  - Form fields for all Goal & Scope elements
  - Save/load functionality
  - Validation for required fields
- Add "Define Goal & Scope" button to main UI
- Show current Goal & Scope in results display

**Files to Modify**:
- `backend/services/openlca_service.py` (lines 1-50: add imports and data classes)
- `backend/app.py` (add new endpoints after line 400)
- `frontend/src/components/GoalScopeForm.jsx` (NEW FILE)
- `frontend/src/App.jsx` (integrate new component)

**Success Criteria**:
- [ ] Users can define and save Goal & Scope before calculations
- [ ] Goal & Scope is displayed with results
- [ ] Functional Unit is properly defined per ISO requirements

---

### 1.2 Data Quality Assessment Framework

**ISO Requirement**: ISO 14044:2006, Section 4.2.3.6 - Data quality requirements shall be specified

**Current Gap**: No tracking of data quality indicators (temporal, geographical, technological coverage, precision, completeness, representativeness)

**Implementation**:

#### Backend Changes (`backend/services/openlca_service.py`)
- Add data quality assessment:
  ```python
  @dataclass
  class DataQuality:
      temporal_coverage: str  # Time period of data
      geographical_coverage: str  # Geographic area
      technological_coverage: str  # Technology represented
      precision: str  # Statistical variation
      completeness: str  # % of data collected vs required
      representativeness: str  # Degree data reflects true population
      consistency: str  # Applied methodology uniformity
      reproducibility: str  # Can results be reproduced?
      data_sources: List[str]
      uncertainty_assessment: Optional[str]
  ```

- Extract data quality from OpenLCA database where available
- Allow manual data quality specification

#### Frontend Changes
- Data quality form within Goal & Scope definition
- Display data quality indicators in results panel
- Color-coded quality indicators (red/yellow/green)

**Files to Modify**:
- `backend/services/openlca_service.py` (add DataQuality class and methods)
- `frontend/src/components/GoalScopeForm.jsx` (add data quality section)
- `frontend/src/components/ResultsPanel.jsx` (display quality indicators)

**Success Criteria**:
- [ ] Data quality can be specified for each study
- [ ] Data quality indicators are displayed with results
- [ ] Users understand the reliability of their results

---

### 1.3 Allocation Documentation

**ISO Requirement**: ISO 14044:2006, Section 4.3.4 - Allocation procedures shall be documented and explained

**Current Gap**: No documentation of how allocation is handled by OpenLCA

**Implementation**:

#### Backend Changes
- Document OpenLCA's default allocation methods
- Allow specification of allocation method in Goal & Scope
- Track and report which allocation method was used

#### Frontend Changes
- Allocation method selection in Goal & Scope form
- Display allocation method used in results

**Files to Modify**:
- `backend/services/openlca_service.py` (track allocation method)
- `backend/app.py` (pass allocation method to calculations)
- `frontend/src/components/ResultsPanel.jsx` (display allocation info)

**Success Criteria**:
- [ ] Allocation method is documented for each calculation
- [ ] Users can choose allocation approach (if supported by OpenLCA)
- [ ] Results clearly show which allocation method was used

---

## Phase 2: Terminology & ISO Compliance

**Priority**: IMMEDIATE
**Estimated Effort**: 25-35 hours

### 2.1 Functional Unit Terminology Fix

**ISO Requirement**: ISO 14040:2006, Section 3.20 - Functional unit is "quantified performance of a product system for use as a reference unit"

**Current Issue**:
- Line 526-529 in `backend/services/openlca_service.py`: Shows "1.0 kg" as functional unit
- Line 126 in `frontend/src/components/ResultsPanel.jsx`: Displays amount, not functional performance

**Fix**:

#### Backend (`backend/services/openlca_service.py`)
Lines 526-529: Change from:
```python
'functional_unit': amount,
'functional_unit_text': f"{amount} {ref_flow_unit}"
```

To:
```python
'functional_unit': {
    'description': f"Production of {amount} {ref_flow_unit} of {product_system_name}",
    'quantified_performance': f"Manufacturing and delivery of product",
    'reference_flow': ref_flow_name,
    'amount': amount,
    'unit': ref_flow_unit
}
```

Also update lines 632-635 similarly.

#### Frontend (`frontend/src/components/ResultsPanel.jsx`)
Line 129: Change from:
```jsx
<span><strong>Functional Unit:</strong> {result.functional_unit_text || `${result.functional_unit} unit(s)`}</span>
```

To:
```jsx
<span><strong>Functional Unit:</strong> {result.functional_unit?.description || result.functional_unit_text || 'Not defined'}</span>
```

**Files to Modify**:
- `backend/services/openlca_service.py:526-529, 632-635`
- `frontend/src/components/ResultsPanel.jsx:129`

**Success Criteria**:
- [ ] Functional unit describes the quantified performance, not just amount
- [ ] Results display properly formatted functional unit
- [ ] Backward compatibility maintained

---

### 2.2 System Boundary Documentation

**ISO Requirement**: ISO 14044:2006, Section 4.2.3.3 - System boundaries shall be determined

**Current Gap**: No explicit documentation of system boundaries

**Implementation**:

#### Backend
- Add system boundary to Goal & Scope data structure
- Extract process tree depth and scope from OpenLCA
- Document cut-off criteria

#### Frontend
- System boundary specification in Goal & Scope form
- Visual system boundary diagram in results
- List of included/excluded processes

**Files to Modify**:
- `backend/services/openlca_service.py` (extract boundary info)
- `frontend/src/components/GoalScopeForm.jsx` (boundary specification)
- `frontend/src/components/ResultsPanel.jsx` (display boundary)

**Success Criteria**:
- [ ] System boundaries are explicitly defined
- [ ] Cut-off criteria are documented
- [ ] Users understand what is included/excluded

---

### 2.3 ISO-Compliant Terminology Updates

**ISO Requirement**: Use standard terminology throughout the application

**Changes Needed**:
- "Process" → "Unit Process" (where appropriate)
- "Product System" → retain (already correct)
- "Impact Category" → "Impact Category" (already correct)
- "Elementary Flow" → add definition and use consistently
- Add tooltips with ISO definitions

**Files to Modify**:
- `backend/app.py` (system prompt, lines 417-532)
- `frontend/src/components/ChatPanel.jsx` (update placeholder text)
- `frontend/src/components/ResultsPanel.jsx` (update labels)

**Success Criteria**:
- [ ] Consistent use of ISO terminology
- [ ] Tooltips provide ISO definitions
- [ ] User-facing language is technically accurate

---

## Phase 3: Life Cycle Interpretation

**Priority**: SHORT-TERM
**Estimated Effort**: 45-60 hours

### 3.1 Identification of Significant Issues

**ISO Requirement**: ISO 14044:2006, Section 4.5.3 - Identify significant issues from LCI and LCIA results

**Implementation**:

#### Backend (`backend/services/openlca_service.py`)
- New method: `identify_significant_issues(results: dict) -> List[SignificantIssue]`
- Analyze results to identify:
  - Life cycle stages with highest contributions
  - Impact categories with highest values
  - Data gaps and quality issues
  - Processes with highest contributions

```python
@dataclass
class SignificantIssue:
    issue_type: str  # 'hotspot', 'data_gap', 'high_uncertainty'
    description: str
    location: str  # Process or life cycle stage
    magnitude: float
    recommendation: str
```

#### Frontend
- New section in ResultsPanel: "Significant Issues Identified"
- Visual highlighting of hotspots
- Recommendations for improvement

**Files to Create/Modify**:
- `backend/services/interpretation.py` (NEW FILE - interpretation logic)
- `backend/services/openlca_service.py` (integrate interpretation)
- `frontend/src/components/InterpretationPanel.jsx` (NEW FILE)

**Success Criteria**:
- [ ] Hotspots automatically identified
- [ ] Significant issues highlighted for user
- [ ] Recommendations provided

---

### 3.2 Evaluation (Completeness, Sensitivity, Consistency)

**ISO Requirement**: ISO 14044:2006, Section 4.5.3.2 - Evaluate completeness, sensitivity, and consistency

**Implementation**:

#### Completeness Check
- Verify all required data is collected
- Identify missing data and assess impact
- Check if system boundaries are appropriate

#### Sensitivity Analysis
- Vary key assumptions and parameters
- Identify which inputs most affect results
- Quantify uncertainty ranges

#### Consistency Check
- Verify methodology applied consistently
- Check for inconsistencies in data quality
- Validate allocation methods

#### Backend (`backend/services/interpretation.py`)
```python
def evaluate_completeness(goal_scope: GoalAndScope, results: dict) -> CompletenessReport
def perform_sensitivity_analysis(baseline_results: dict, parameters: List[Parameter]) -> SensitivityReport
def check_consistency(results: dict, goal_scope: GoalAndScope) -> ConsistencyReport
```

#### Frontend
- Interpretation dashboard with three tabs: Completeness, Sensitivity, Consistency
- Interactive sensitivity analysis
- Consistency checklist with pass/fail indicators

**Files to Create/Modify**:
- `backend/services/interpretation.py` (add evaluation methods)
- `frontend/src/components/InterpretationPanel.jsx` (add evaluation displays)

**Success Criteria**:
- [ ] Completeness evaluated and reported
- [ ] Sensitivity analysis available
- [ ] Consistency checked automatically

---

### 3.3 Conclusions, Limitations & Recommendations

**ISO Requirement**: ISO 14044:2006, Section 4.5.3.3 - Draw conclusions, describe limitations, and provide recommendations

**Implementation**:

#### Backend
- Generate conclusions based on significant issues
- Document limitations from data quality and assumptions
- Provide recommendations for:
  - Improving product system
  - Reducing environmental impacts
  - Further study areas

#### Frontend
- Final interpretation summary panel
- Limitations clearly stated
- Actionable recommendations
- Export capability

**Files to Modify**:
- `backend/services/interpretation.py` (conclusion generation)
- `frontend/src/components/InterpretationPanel.jsx` (display conclusions)

**Success Criteria**:
- [ ] Conclusions drawn from analysis
- [ ] Limitations clearly documented
- [ ] Recommendations provided to user

---

## Phase 4: Reporting & Critical Review

**Priority**: MEDIUM-TERM
**Estimated Effort**: 30-40 hours

### 4.1 ISO-Compliant Report Generation

**ISO Requirement**: ISO 14044:2006, Section 5 - Report format and content requirements

**Implementation**:

#### Report Sections (per ISO 14044:2006, Table 1)
1. General information about the study
2. Goal of the study
3. Scope of the study
4. Life cycle inventory analysis
5. Life cycle impact assessment
6. Life cycle interpretation
7. Critical review (if performed)
8. References

#### Backend (`backend/services/report_generator.py` - NEW FILE)
```python
class ISOReportGenerator:
    def generate_full_report(self, study_id: str) -> bytes  # PDF
    def generate_html_report(self, study_id: str) -> str
    def generate_markdown_report(self, study_id: str) -> str
```

#### Frontend
- "Generate ISO Report" button
- Report preview
- Download options (PDF, HTML, Markdown)

**Files to Create**:
- `backend/services/report_generator.py` (NEW FILE)
- `backend/templates/iso_report_template.html` (NEW FILE)
- Frontend: Add button to ResultsPanel

**Success Criteria**:
- [ ] Reports include all ISO-required sections
- [ ] Reports are well-formatted and professional
- [ ] Users can download and share reports

---

### 4.2 Critical Review Workflow

**ISO Requirement**: ISO 14044:2006, Section 6 - Critical review required for public comparative assertions

**Implementation**:

#### Backend
- Track studies that require critical review
- Provide critical review checklist
- Document review findings

#### Frontend
- Critical review flag in Goal & Scope
- Review checklist interface
- Review status tracking

**Note**: This is preparatory work for future critical reviews, not full implementation of review process

**Files to Create/Modify**:
- `backend/services/openlca_service.py` (add critical_review_required flag)
- `frontend/src/components/GoalScopeForm.jsx` (add review flag)

**Success Criteria**:
- [ ] Studies can be flagged for critical review
- [ ] ISO critical review checklist available
- [ ] Foundation laid for external review process

---

## Phase 5: UI/UX Enhancements

**Priority**: MEDIUM-TERM
**Estimated Effort**: 25-30 hours

### 5.1 Results Panel Enhancements

**Current Issues**:
- Missing system boundary display
- No data quality indicators
- No allocation information
- No assumptions/limitations display

**Enhancements**:

#### System Information Section
```jsx
<div className="system-info-panel">
  <h3>Study Information</h3>
  <div className="info-grid">
    <InfoCard title="Functional Unit" content={...} />
    <InfoCard title="System Boundary" content={...} />
    <InfoCard title="Data Quality" content={...} quality={qualityScore} />
    <InfoCard title="Allocation" content={...} />
  </div>
</div>
```

#### Assumptions & Limitations Section
```jsx
<div className="assumptions-panel">
  <h3>Assumptions & Limitations</h3>
  <ul>
    {assumptions.map(a => <li key={a.id}>{a.text}</li>)}
  </ul>
</div>
```

**Files to Modify**:
- `frontend/src/components/ResultsPanel.jsx` (add new sections)
- `frontend/src/components/ResultsPanel.css` (styling)

**Success Criteria**:
- [ ] All ISO-required information displayed
- [ ] Clear, professional layout
- [ ] Easy to understand for non-experts

---

### 5.2 Goal & Scope Definition Form (New Component)

**Component Structure**:
```
GoalScopeForm.jsx
├── StudyGoalSection
├── FunctionalUnitSection
├── SystemBoundarySection
├── DataQualitySection
├── AssumptionsSection
└── AllocationSection
```

**Features**:
- Step-by-step wizard interface
- Validation for required fields
- Save/load functionality
- Help text with ISO guidance

**Files to Create**:
- `frontend/src/components/GoalScopeForm.jsx` (NEW)
- `frontend/src/components/GoalScopeForm.css` (NEW)

**Success Criteria**:
- [ ] Intuitive form for Goal & Scope definition
- [ ] All ISO-required fields present
- [ ] Help text guides users

---

### 5.3 Interpretation Dashboard (New Component)

**Component Structure**:
```
InterpretationPanel.jsx
├── SignificantIssuesTab
│   ├── HotspotsView
│   └── DataGapsView
├── EvaluationTab
│   ├── CompletenessCheck
│   ├── SensitivityAnalysis
│   └── ConsistencyCheck
└── ConclusionsTab
    ├── KeyFindings
    ├── Limitations
    └── Recommendations
```

**Features**:
- Interactive visualizations
- Downloadable interpretation report
- Actionable recommendations

**Files to Create**:
- `frontend/src/components/InterpretationPanel.jsx` (NEW)
- `frontend/src/components/InterpretationPanel.css` (NEW)

**Success Criteria**:
- [ ] Interpretation results clearly presented
- [ ] Interactive exploration of findings
- [ ] Export capability

---

## Phase 6: AI Assistant Improvements

**Priority**: LONG-TERM
**Estimated Effort**: 10-15 hours

### 6.1 ISO-Aware System Prompt

**Current Issue**: System prompt (lines 417-532 in `backend/app.py`) doesn't guide users through ISO-required steps

**Updated Prompt Structure**:
```python
system_prompt = f"""You are an expert Life Cycle Assessment (LCA) assistant following ISO 14040:2006 and ISO 14044:2006 standards.

# ISO 14040/14044 Workflow

An ISO-compliant LCA study follows these phases:

1. **Goal and Scope Definition** (ISO 14044:2006, Section 4.2)
   - Define study goal, intended application, and audience
   - Define functional unit (quantified performance of product system)
   - Define system boundary and cut-off criteria
   - Specify data quality requirements
   - Document assumptions and limitations

2. **Life Cycle Inventory Analysis** (LCI) (ISO 14044:2006, Section 4.3)
   - Collect data for all unit processes
   - Calculate inventory results
   - Document allocation procedures

3. **Life Cycle Impact Assessment** (LCIA) (ISO 14044:2006, Section 4.4)
   - Select impact categories and methods
   - Classify inventory results to impact categories
   - Calculate category indicator results

4. **Life Cycle Interpretation** (ISO 14044:2006, Section 4.5)
   - Identify significant issues
   - Evaluate completeness, sensitivity, consistency
   - Draw conclusions and provide recommendations

# Your Role

Guide users through this ISO workflow. For each calculation:
1. First ensure Goal & Scope is defined
2. Explain the functional unit in terms of quantified performance
3. Clarify system boundaries
4. After showing results, provide interpretation
5. Identify hotspots and recommendations
6. Always use ISO-compliant terminology

# Available Database: ELCD
{db_summary}

# ISO Terminology
- **Functional Unit**: Quantified performance of a product system (not just an amount)
- **Reference Flow**: Measure of outputs from processes to fulfill functional unit
- **System Boundary**: Set of criteria for unit processes included in product system
- **Elementary Flow**: Material/energy entering from or leaving to environment
- **Unit Process**: Smallest element for which data are collected
- **Allocation**: Partitioning input/output flows of a process between product systems

Always maintain ISO compliance and guide users through proper LCA methodology.
"""
```

**Files to Modify**:
- `backend/app.py:417-532` (replace system prompt)

**Success Criteria**:
- [ ] Assistant guides users through ISO workflow
- [ ] ISO terminology used consistently
- [ ] Users understand ISO requirements

---

### 6.2 Interpretation Intelligence

**Feature**: AI assistant provides interpretation suggestions

**Implementation**:
- Analyze calculation results
- Provide context-aware interpretation
- Suggest sensitivity analyses
- Recommend improvements

**Example Interactions**:
- "I notice your glass fiber production has high energy consumption. Would you like to explore renewable energy scenarios?"
- "The data quality for this upstream process is low. Consider collecting primary data for more accurate results."

**Files to Modify**:
- `backend/app.py` (enhance chat logic)
- `backend/services/interpretation.py` (add AI-friendly interpretation summaries)

**Success Criteria**:
- [ ] Assistant provides intelligent interpretation help
- [ ] Suggestions are contextually relevant
- [ ] Users receive actionable guidance

---

## Priority Matrix

| Priority | Phase | Features |
|----------|-------|----------|
| **IMMEDIATE** | Phase 1 | Goal & Scope, Data Quality, Allocation |
| **IMMEDIATE** | Phase 2 | Functional Unit fix, System Boundary, Terminology |
| **SHORT-TERM** | Phase 3 | Life Cycle Interpretation (all) |
| **MEDIUM-TERM** | Phase 4 | ISO Reporting, Critical Review prep |
| **MEDIUM-TERM** | Phase 5 | UI/UX Enhancements |
| **LONG-TERM** | Phase 6 | AI Assistant improvements |

---

## Testing Strategy

### After Each Phase:

1. **Unit Tests**
   - Test new backend functions
   - Test data structure validation
   - Test API endpoints

2. **Integration Tests**
   - Test full workflow from frontend to backend
   - Test data persistence
   - Test calculation pipeline

3. **ISO Compliance Tests**
   - Verify all ISO-required elements present
   - Validate terminology usage
   - Check report completeness

4. **User Acceptance Tests**
   - Test with real LCA scenarios
   - Verify usability
   - Gather feedback

### Test Files to Create:
- `backend/tests/test_goal_scope.py`
- `backend/tests/test_interpretation.py`
- `backend/tests/test_report_generation.py`
- `backend/tests/test_iso_compliance.py`

---

## Documentation Requirements

### For Each Phase:

1. **Code Documentation**
   - Docstrings with ISO references
   - Inline comments explaining ISO compliance
   - Type hints for all functions

2. **User Documentation**
   - User guide updates
   - ISO concept explanations
   - Workflow tutorials

3. **Developer Documentation**
   - Architecture decisions
   - API documentation
   - Integration notes

### Documentation Files:
- `docs/ISO_COMPLIANCE.md` - How app meets ISO standards
- `docs/USER_GUIDE.md` - Updated with ISO workflow
- `docs/API_REFERENCE.md` - All endpoints documented
- `docs/DEVELOPMENT.md` - Setup and contribution guide

---

## Success Criteria

### Overall ISO Compliance Checklist:

**ISO 14040:2006 - Principles and Framework**
- [ ] Four phases implemented (Goal/Scope, LCI, LCIA, Interpretation)
- [ ] Iterative nature supported
- [ ] Transparency maintained
- [ ] Comprehensiveness ensured
- [ ] Priority of scientific approach
- [ ] Environmental focus maintained

**ISO 14044:2006 - Requirements and Guidelines**
- [ ] Goal and Scope requirements met (Section 4.2)
- [ ] LCI requirements met (Section 4.3)
- [ ] LCIA requirements met (Section 4.4)
- [ ] Interpretation requirements met (Section 4.5)
- [ ] Reporting requirements met (Section 5)
- [ ] Critical review preparedness (Section 6)

**Functional Requirements**
- [ ] All calculations ISO-compliant
- [ ] Proper terminology throughout
- [ ] Complete traceability
- [ ] Reproducible results
- [ ] Export capability
- [ ] User guidance

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenLCA API limitations | High | Research API capabilities early, document constraints |
| Complex UI overwhelming users | Medium | Progressive disclosure, help text, tutorials |
| Performance impact of interpretation | Medium | Async processing, caching, optional features |
| Breaking changes to existing workflows | High | Maintain backward compatibility, migration guide |
| Incomplete ISO understanding | High | Reference ISO documents throughout, seek expert review |

---

## Next Steps

1. **Save this plan** ✓
2. **Set up GitHub** (next task)
3. **Begin Phase 1** (after Git setup)
4. **Test Phase 1**
5. **Get user approval**
6. **Continue to Phase 2**

---

## References

- ISO 14040:2006 - Environmental management -- Life cycle assessment -- Principles and framework
- ISO 14044:2006 - Environmental management -- Life cycle assessment -- Requirements and guidelines
- OpenLCA Documentation: https://www.openlca.org/
- ELCD Database Documentation

---

*Plan created: 2025-11-01*
*Last updated: 2025-11-01*
*Status: Ready for Phase 1 implementation*
