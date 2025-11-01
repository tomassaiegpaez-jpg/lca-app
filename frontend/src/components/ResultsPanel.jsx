import { useState } from 'react'
import './ResultsPanel.css'

function ResultsPanel({ results }) {
  const [activeTab, setActiveTab] = useState(0)
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })

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
