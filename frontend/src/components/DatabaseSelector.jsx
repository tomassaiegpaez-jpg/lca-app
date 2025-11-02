import { useState, useEffect } from 'react'
import './DatabaseSelector.css'

function DatabaseSelector({ selectedDatabase, onDatabaseChange }) {
  const [databases, setDatabases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchDatabases()
  }, [])

  const fetchDatabases = async () => {
    try {
      console.log('[DatabaseSelector] Fetching from http://localhost:8000/api/databases')
      const response = await fetch('http://localhost:8000/api/databases')
      console.log('[DatabaseSelector] Response status:', response.status)

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch databases`)
      }

      const data = await response.json()
      console.log('[DatabaseSelector] Received data:', data)

      if (!data.databases || !Array.isArray(data.databases)) {
        throw new Error('Invalid response format - expected databases array')
      }

      setDatabases(data.databases)
      setError(null)
      console.log('[DatabaseSelector] Successfully loaded', data.databases.length, 'databases')
    } catch (err) {
      console.error('[DatabaseSelector] Error details:', err)
      setError(`Unable to load databases: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const dbId = e.target.value
    const db = databases.find(d => d.id === dbId)

    // Check if database is available before switching
    if (db && !db.available) {
      alert(`Database "${db.name}" is not available. Please import it in openLCA and start the IPC server on port ${db.port}.`)
      return
    }

    onDatabaseChange(dbId)
  }

  if (loading) {
    return <div className="database-selector loading">Loading databases...</div>
  }

  if (error) {
    return <div className="database-selector error">{error}</div>
  }

  // Get currently selected database info
  const currentDb = databases.find(d => d.id === selectedDatabase)

  return (
    <div className="database-selector">
      <label htmlFor="database-select">Database:</label>
      <select
        id="database-select"
        value={selectedDatabase}
        onChange={handleChange}
      >
        {databases.map(db => (
          <option
            key={db.id}
            value={db.id}
            disabled={!db.available}
          >
            {db.name} {!db.available && '(offline)'}
          </option>
        ))}
      </select>

      {currentDb && (
        <div className="database-info">
          <span className={`status-indicator ${currentDb.available ? 'online' : 'offline'}`}>
            {currentDb.available ? '●' : '○'}
          </span>
          <span className="database-type">{currentDb.type}</span>
          {currentDb.requires_license && (
            <span className="license-indicator" title="License required">
              🔒
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export default DatabaseSelector
