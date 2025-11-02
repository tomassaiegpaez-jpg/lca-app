import { useState, useEffect } from 'react'
import './MethodSelector.css'

function MethodSelector({ selectedDatabase, selectedMethod, onMethodChange }) {
  const [methods, setMethods] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Fetch methods when database changes
  useEffect(() => {
    if (selectedDatabase) {
      fetchMethods(selectedDatabase)
    }
  }, [selectedDatabase])

  const fetchMethods = async (databaseId) => {
    setLoading(true)
    try {
      console.log(`[MethodSelector] Fetching methods for database: ${databaseId}`)
      const response = await fetch(`http://localhost:8000/api/databases/${databaseId}/methods`)
      console.log('[MethodSelector] Response status:', response.status)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch methods`)
      }

      const data = await response.json()
      console.log('[MethodSelector] Received data:', data)

      if (!data.methods || !Array.isArray(data.methods)) {
        throw new Error('Invalid response format - expected methods array')
      }

      setMethods(data.methods)
      setError(null)
      console.log('[MethodSelector] Successfully loaded', data.methods.length, 'methods')
    } catch (err) {
      console.error('[MethodSelector] Error details:', err)
      setError(`Unable to load methods: ${err.message}`)
      setMethods([])
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const methodId = e.target.value
    // Empty string means "Auto (AI will choose)"
    onMethodChange(methodId === '' ? null : methodId)
  }

  if (loading) {
    return <div className="method-selector loading">Loading methods...</div>
  }

  if (error) {
    return <div className="method-selector error">{error}</div>
  }

  // Get currently selected method info
  const currentMethod = methods.find(m => m.id === selectedMethod)

  return (
    <div className="method-selector">
      <label htmlFor="method-select">Impact Method:</label>
      <select
        id="method-select"
        value={selectedMethod || ''}
        onChange={handleChange}
      >
        <option value="">Auto (AI will choose)</option>
        {methods.map(method => (
          <option
            key={method.id}
            value={method.id}
          >
            {method.name}
          </option>
        ))}
      </select>

      {currentMethod && (
        <div className="method-info">
          <span className="method-indicator" title="User-selected method">
            ✓
          </span>
        </div>
      )}
      {!currentMethod && (
        <div className="method-info">
          <span className="method-indicator-auto" title="AI will recommend method">
            🤖
          </span>
        </div>
      )}
    </div>
  )
}

export default MethodSelector
