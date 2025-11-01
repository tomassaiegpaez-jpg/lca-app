import { useState } from 'react'
import './ResultsPanel.css'

function ResultsPanel({ results }) {
  const [activeTab, setActiveTab] = useState(0)
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [showGoalScope, setShowGoalScope] = useState(false)

  // Render goal and scope summary - always shown, AI-inferred
  const renderGoalScopeSummary = (goalScope) => {
    if (!goalScope) {
      return (
        <div className="goal-scope-summary incomplete">
          <div className="goal-scope-header">
            <h3>ISO 14044 Goal & Scope Definition</h3>
          </div>
          <p className="goal-scope-note">Goal & Scope was not fully inferred from the analysis. Some ISO 14044 elements may be missing.</p>
        </div>
      )
    }

    return (
      <div className="goal-scope-summary">
        <div className="goal-scope-header">
          <h3>Study Goal & Scope</h3>
          <button
            className="toggle-details"
            onClick={() => setShowGoalScope(!showGoalScope)}
          >
            {showGoalScope ? 'Hide Details' : 'Show Details'}
          </button>
        </div>

        <div className="goal-scope-brief">
          <p><strong>Study Goal:</strong> {goalScope.study_goal || 'Not specified'}</p>
          <p><strong>Functional Unit:</strong> {goalScope.functional_unit?.description || 'Not specified'}</p>
          <p><strong>Impact Method:</strong> {goalScope.impact_method || 'Not specified'}</p>
          {goalScope.inferred && <p className="inferred-note">ℹ️ <em>Automatically defined from your request</em></p>}
        </div>

        {showGoalScope && (
          <div className="goal-scope-details">
            <div className="detail-section">
              <h4>Study Information</h4>
              <p><strong>Reasons:</strong> {goalScope.reasons_for_study}</p>
              <p><strong>Intended Audience:</strong> {goalScope.intended_audience}</p>
              <p><strong>Comparative Assertion:</strong> {goalScope.comparative_assertion ? 'Yes' : 'No'}</p>
            </div>

            <div className="detail-section">
              <h4>Functional Unit</h4>
              <p className="help-text">What product or service does this study measure?</p>
              <p><strong>Description:</strong> {goalScope.functional_unit.description}</p>
              <p><strong>Performance:</strong> {goalScope.functional_unit.quantified_performance}</p>
              <p><strong>Reference Flow:</strong> {goalScope.functional_unit.reference_flow} - {goalScope.functional_unit.amount} {goalScope.functional_unit.unit}</p>
            </div>

            <div className="detail-section">
              <h4>System Boundary</h4>
              <p className="help-text">What's included and excluded from this analysis?</p>
              <p><strong>Description:</strong> {goalScope.system_boundary.description}</p>
              <p><strong>Cut-off Criteria:</strong> {goalScope.system_boundary.cut_off_criteria}</p>
              {goalScope.system_boundary.included_processes.length > 0 && (
                <div>
                  <strong>Included:</strong>
                  <ul>
                    {goalScope.system_boundary.included_processes.map((proc, i) => (
                      <li key={i}>{proc}</li>
                    ))}
                  </ul>
                </div>
              )}
              {goalScope.system_boundary.excluded_processes.length > 0 && (
                <div>
                  <strong>Excluded:</strong>
                  <ul>
                    {goalScope.system_boundary.excluded_processes.map((proc, i) => (
                      <li key={i}>{proc}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="detail-section">
              <h4>Data Quality</h4>
              <p className="help-text">How reliable is the underlying data?</p>
              <div className="quality-grid">
                <div><strong>Time Period:</strong> {goalScope.data_quality_requirements.temporal_coverage}</div>
                <div><strong>Geography:</strong> {goalScope.data_quality_requirements.geographical_coverage}</div>
                <div><strong>Technology:</strong> {goalScope.data_quality_requirements.technological_coverage}</div>
                <div><strong>Precision:</strong> {goalScope.data_quality_requirements.precision}</div>
                <div><strong>Completeness:</strong> {goalScope.data_quality_requirements.completeness}</div>
                <div><strong>Representativeness:</strong> {goalScope.data_quality_requirements.representativeness}</div>
                <div><strong>Consistency:</strong> {goalScope.data_quality_requirements.consistency}</div>
                <div><strong>Reproducibility:</strong> {goalScope.data_quality_requirements.reproducibility}</div>
              </div>
            </div>

            {goalScope.assumptions.length > 0 && (
              <div className="detail-section">
                <h4>Assumptions</h4>
                <ul>
                  {goalScope.assumptions.map((assumption, i) => (
                    <li key={i}>{assumption}</li>
                  ))}
                </ul>
              </div>
            )}

            {goalScope.limitations.length > 0 && (
              <div className="detail-section">
                <h4>Limitations</h4>
                <ul>
                  {goalScope.limitations.map((limitation, i) => (
                    <li key={i}>{limitation}</li>
                  ))}
                </ul>
              </div>
            )}

            {goalScope.allocation_rules.length > 0 && (
              <div className="detail-section">
                <h4>Allocation Rules</h4>
                <ul>
                  {goalScope.allocation_rules.map((rule, i) => (
                    <li key={i}>{rule}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    )
  }

  // Build ASCII tree diagram from process network data
  const buildASCIITree = (diagramData) => {
    if (!diagramData || !diagramData.nodes || !diagramData.edges) {
      return 'No diagram data available'
    }

    const { nodes, edges, reference_process_id } = diagramData

    // Build adjacency map: recipient_id -> [{provider_id, flow_name}]
    const suppliers = {}
    edges.forEach(edge => {
      if (!suppliers[edge.to]) suppliers[edge.to] = []
      suppliers[edge.to].push({
        provider_id: edge.from,
        flow_name: edge.label
      })
    })

    // Build node lookup map
    const nodeMap = {}
    nodes.forEach(node => {
      nodeMap[node.id] = node.label
    })

    // Recursive tree builder with cycle detection
    const buildTree = (processId, visited = new Set(), indent = 0, isLast = true, prefix = '') => {
      if (visited.has(processId)) return ''
      visited.add(processId)

      const processName = nodeMap[processId] || 'Unknown Process'
      let result = ''

      if (indent === 0) {
        // Root node (reference process)
        result += `${processName} [REFERENCE]\n`
      } else {
        // Child nodes
        const connector = isLast ? '└── ' : '├── '
        result += `${prefix}${connector}${processName}\n`
      }

      const processSuppliers = suppliers[processId] || []
      processSuppliers.forEach((supplier, i) => {
        const isLastSupplier = i === processSuppliers.length - 1
        const extension = isLast ? '    ' : '│   '
        const flowConnector = isLastSupplier ? '└── ' : '├── '
        const currentPrefix = indent === 0 ? '' : prefix + extension

        // Show flow name
        result += `${currentPrefix}${flowConnector}[${supplier.flow_name}]\n`

        // Recurse for supplier process
        const newPrefix = currentPrefix + (isLastSupplier ? '    ' : '│   ')
        result += buildTree(supplier.provider_id, visited, indent + 1, isLastSupplier, newPrefix)
      })

      return result
    }

    if (!reference_process_id) {
      return 'No reference process found'
    }

    return buildTree(reference_process_id)
  }

  // No results - show empty state
  if (!results || results.length === 0) {
    return (
      <div className="results-panel">
        <div className="empty-state">
          <div className="empty-icon">📊</div>
          <h2>No Results Yet</h2>
          <p>Ask the assistant to calculate environmental impacts</p>
          <p className="hint">Try: "Calculate the impact for glass fiber production"</p>
        </div>
      </div>
    )
  }

  // Determine if we should show comparison view
  const showComparison = results.length > 1 && activeTab === results.length

  // Handle table sorting
  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }
    setSortConfig({ key, direction })
  }

  const getSortedImpacts = (impacts) => {
    if (!sortConfig.key) return impacts

    return [...impacts].sort((a, b) => {
      let aVal = a[sortConfig.key]
      let bVal = b[sortConfig.key]

      if (sortConfig.key === 'amount') {
        aVal = parseFloat(aVal)
        bVal = parseFloat(bVal)
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1
      return 0
    })
  }

  // Render single result view
  const renderSingleResult = (result, index) => {
    const sortedImpacts = getSortedImpacts(result.impacts || [])

    return (
      <div className="result-view" key={index}>
        {/* Goal & Scope Summary - Always shown, AI-inferred */}
        {renderGoalScopeSummary(result.goal_scope)}

        {/* Functional Unit Header */}
        <div className="functional-unit-header">
          <h2>{result.product_system || `Process ${result.process_id?.substring(0, 8)}`}</h2>
          <div className="result-meta">
            <span><strong>Method:</strong> {result.impact_method}</span>
            <span><strong>Functional Unit:</strong> {result.functional_unit_text || `${result.functional_unit} unit(s)`}</span>
            <span><strong>Mode:</strong> {result.calculation_mode}</span>
          </div>
        </div>

        {/* Warning if present */}
        {result.warning && (
          <div className="warning-box">
            <strong>⚠️ Warning:</strong> {result.warning}
          </div>
        )}

        {/* Impact Categories Table */}
        {sortedImpacts.length > 0 ? (
          <div className="impact-table-container">
            <div className="table-header">
              <h3>Impact Categories ({sortedImpacts.length})</h3>
            </div>
            <table className="impact-table">
              <thead>
                <tr>
                  <th onClick={() => handleSort('category')} className="sortable">
                    Category {sortConfig.key === 'category' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th onClick={() => handleSort('amount')} className="sortable">
                    Amount {sortConfig.key === 'amount' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                  </th>
                  <th>Unit</th>
                </tr>
              </thead>
              <tbody>
                {sortedImpacts.map((impact, i) => (
                  <tr key={i}>
                    <td className="category-name">{impact.category}</td>
                    <td className="impact-value">{impact.amount.toExponential(3)}</td>
                    <td className="impact-unit">{impact.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-impacts">
            <p>No impact data available</p>
          </div>
        )}

        {/* Product System Diagram */}
        {result.diagram && result.diagram.nodes && result.diagram.nodes.length > 0 && (
          <div className="process-diagram-container">
            <div className="diagram-header">
              <h3>Product System Diagram</h3>
              <span className="diagram-stats">
                {result.diagram.metadata.total_processes} processes, {result.diagram.metadata.total_links} links
              </span>
            </div>
            <div className="ascii-diagram">
              <pre>{buildASCIITree(result.diagram)}</pre>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Render comparison view
  const renderComparisonView = () => {
    // Find common impact categories across all results
    const categoryMap = new Map()

    results.forEach((result, resultIndex) => {
      (result.impacts || []).forEach(impact => {
        if (!categoryMap.has(impact.category)) {
          categoryMap.set(impact.category, {
            category: impact.category,
            unit: impact.unit,
            values: new Array(results.length).fill(null)
          })
        }
        categoryMap.get(impact.category).values[resultIndex] = impact.amount
      })
    })

    const comparisonData = Array.from(categoryMap.values())

    return (
      <div className="comparison-view">
        <div className="comparison-header">
          <h2>Comparison of {results.length} Results</h2>
          <p>Comparing impact categories across all calculations</p>
        </div>

        <div className="comparison-table-container">
          <table className="comparison-table">
            <thead>
              <tr>
                <th>Impact Category</th>
                <th>Unit</th>
                {results.map((result, i) => (
                  <th key={i} className="result-column">
                    Result {i + 1}
                    <div className="result-name">{result.product_system || 'Process'}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {comparisonData.map((row, i) => (
                <tr key={i}>
                  <td className="category-name">{row.category}</td>
                  <td className="impact-unit">{row.unit}</td>
                  {row.values.map((value, j) => (
                    <td key={j} className="impact-value">
                      {value !== null ? value.toExponential(3) : '—'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  return (
    <div className="results-panel">
      {/* Tabs */}
      <div className="tabs">
        {results.map((result, i) => (
          <button
            key={i}
            className={`tab ${activeTab === i ? 'active' : ''}`}
            onClick={() => setActiveTab(i)}
          >
            Result {i + 1}
          </button>
        ))}
        {results.length > 1 && (
          <button
            className={`tab comparison-tab ${activeTab === results.length ? 'active' : ''}`}
            onClick={() => setActiveTab(results.length)}
          >
            Compare All
          </button>
        )}
      </div>

      {/* Content */}
      <div className="results-content">
        {showComparison ? renderComparisonView() : renderSingleResult(results[activeTab], activeTab)}
      </div>
    </div>
  )
}

export default ResultsPanel
