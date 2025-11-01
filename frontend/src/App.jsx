import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import ResultsPanel from './components/ResultsPanel'
import GoalScopeForm from './components/GoalScopeForm'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [conversationId, setConversationId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [lciaResults, setLciaResults] = useState([]) // Array of LCIA results
  const [showGoalScopeForm, setShowGoalScopeForm] = useState(false)
  const [currentGoalScope, setCurrentGoalScope] = useState(null)

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
          conversation_id: conversationId
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

      // If LCIA calculation was successful, add to results panel
      if (data.action && data.action.results &&
          (data.action.type === 'calculate_lcia' || data.action.type === 'calculate_lcia_ps')) {
        setLciaResults(prev => [...prev, {
          ...data.action.results,
          timestamp: new Date().toISOString()
        }])
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

  const handleOpenGoalScope = () => {
    setShowGoalScopeForm(true)
  }

  const handleSaveGoalScope = (goalScopeData) => {
    setCurrentGoalScope(goalScopeData)
    setShowGoalScopeForm(false)
  }

  const handleCancelGoalScope = () => {
    setShowGoalScopeForm(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>LCA Assistant</h1>
            <p>Life Cycle Assessment powered by OpenLCA & Claude AI</p>
          </div>
          <button onClick={handleOpenGoalScope} className="btn-define-goal">
            Define Goal & Scope
          </button>
        </div>
      </header>

      <div className="app-layout">
        <ChatPanel
          messages={messages}
          loading={loading}
          onSendMessage={handleSendMessage}
        />
        <ResultsPanel results={lciaResults} goalScope={currentGoalScope} />
      </div>

      {showGoalScopeForm && (
        <GoalScopeForm
          onSave={handleSaveGoalScope}
          onCancel={handleCancelGoalScope}
          initialData={currentGoalScope}
        />
      )}
    </div>
  )
}

export default App
