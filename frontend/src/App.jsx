import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import ResultsPanel from './components/ResultsPanel'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lciaResults, setLciaResults] = useState([]) // Array of LCIA results with Goal & Scope
  const [selectedDatabase, setSelectedDatabase] = useState('elcd') // Default to ELCD
  const [selectedMethod, setSelectedMethod] = useState(null) // LCIA method: null = Auto (AI will choose)
  const [methodSelectionMode, setMethodSelectionMode] = useState('auto') // 'manual' or 'auto'

  const handleDatabaseChange = (databaseId) => {
    setSelectedDatabase(databaseId)
    // Don't reset conversation - backend will track database change in conversation context
  }

  const handleMethodChange = (methodId) => {
    setSelectedMethod(methodId)
    setMethodSelectionMode(methodId === null ? 'auto' : 'manual')
    // Don't reset conversation when changing method - just affects next calculation
  }

  const handleSendMessage = async (userMessage) => {
    setLoading(true)

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])

    try {
      const response = await fetch('http://localhost:8000/api/lca/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          conversation_id: conversationId,
          database_id: selectedDatabase,
          preferred_method_id: selectedMethod
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Server error (${response.status}): ${errorText}`)
      }

      const data = await response.json()

      // Set conversation ID if this is the first message
      if (!conversationId) {
        setConversationId(data.conversation_id)
      }

      // Add assistant response to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.message,
        action: data.action
      }])

      // If LCIA calculation was successful, add to results panel with Goal & Scope
      if (data.action && data.action.results &&
          (data.action.type === 'calculate_lcia' || data.action.type === 'calculate_lcia_ps')) {
        setLciaResults(prev => [...prev, {
          ...data.action.results,
          timestamp: new Date().toISOString(),
          goal_scope: data.action.results.goal_scope || null // AI-inferred Goal & Scope
        }])

        // Update UI to reflect the method that was actually used (only if in auto selection mode)
        if (data.action.results.used_method_id && methodSelectionMode === 'auto') {
          setSelectedMethod(data.action.results.used_method_id)
        }
      }

    } catch (error) {
      console.error('Fetch error:', error)
      setMessages(prev => [...prev, {
        role: 'error',
        content: `Error: ${error.message}`
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-text">
            <h1>LCA Assistant</h1>
            <p>Life Cycle Assessment powered by OpenLCA & Claude AI</p>
          </div>
        </div>
      </header>

      <div className="app-layout">
        <ChatPanel
          messages={messages}
          loading={loading}
          onSendMessage={handleSendMessage}
          selectedDatabase={selectedDatabase}
          onDatabaseChange={handleDatabaseChange}
          selectedMethod={selectedMethod}
          onMethodChange={handleMethodChange}
          methodSelectionMode={methodSelectionMode}
          conversationId={conversationId}
        />
        <ResultsPanel results={lciaResults} />
      </div>
    </div>
  )
}

export default App
