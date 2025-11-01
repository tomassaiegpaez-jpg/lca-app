import { useState } from 'react'
import './ChatPanel.css'

function ChatPanel({ messages, loading, onSendMessage }) {
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return
    onSendMessage(input)
    setInput('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>Welcome to LCA Assistant!</h2>
            <p>I can help you assess the environmental impact of products and processes.</p>
            <p>Try asking: "I want to assess the environmental impact of producing 1kg of glass fiber"</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">
              {msg.content}
            </div>

            {/* Show action status for search results */}
            {msg.action && msg.action.type && msg.action.type.startsWith('search') && (
              <div className="action-feedback">
                {msg.action.results && msg.action.results.length > 0 ? (
                  <div className="search-results-inline">
                    <strong>✓ Found {msg.action.results.length} {msg.action.type === 'search_processes' ? 'processes' : 'product systems'}:</strong>
                    <ul className="inline-results-list">
                      {msg.action.results.slice(0, 3).map((item, i) => (
                        <li key={i}>{item.name}</li>
                      ))}
                      {msg.action.results.length > 3 && <li>...and {msg.action.results.length - 3} more</li>}
                    </ul>
                  </div>
                ) : (
                  <div className="search-results-inline warning">
                    <strong>⚠️ Found 0 results</strong> - Try different keywords or check spelling
                  </div>
                )}
              </div>
            )}

            {/* Show LCIA calculation status */}
            {msg.action && (msg.action.type === 'calculate_lcia' || msg.action.type === 'calculate_lcia_ps') && (
              <div className="action-feedback">
                {msg.action.results ? (
                  <>
                    <strong>✓ Calculation complete - Results displayed in panel →</strong>
                    {msg.action.results.warning && (
                      <div className="search-results-inline warning" style={{marginTop: '0.5rem'}}>
                        {msg.action.results.warning}
                      </div>
                    )}
                  </>
                ) : msg.action.error ? (
                  <span className="error-inline">⚠️ {msg.action.error}</span>
                ) : null}
              </div>
            )}

            {/* Show generic action errors */}
            {msg.action && msg.action.error && !msg.action.type?.startsWith('calculate') && (
              <div className="action-feedback">
                <span className="error-inline">⚠️ {msg.action.error}</span>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="message assistant loading">
            <div className="message-content">Thinking...</div>
          </div>
        )}
      </div>

      <div className="input-area">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe the LCA you want to perform..."
          disabled={loading}
          rows={3}
        />
        <button onClick={handleSend} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}

export default ChatPanel
