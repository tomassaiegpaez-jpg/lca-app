import './ConversationHeader.css'

function ConversationHeader({
  database,
  method,
  methodSelectionMode,
  conversationId
}) {
  return (
    <div className="conversation-header">
      <div className="conversation-context">
        <div className="context-item">
          <span className="context-label">Database:</span>
          <span className="context-value">{database}</span>
        </div>

        <div className="context-item">
          <span className="context-label">Method:</span>
          <span className="context-value">
            {method || 'Auto (AI will choose)'}
            {methodSelectionMode === 'manual' && method && (
              <span className="mode-indicator manual" title="User-selected method">
                👤
              </span>
            )}
            {methodSelectionMode === 'auto' && (
              <span className="mode-indicator auto" title="AI-recommended method">
                🤖
              </span>
            )}
          </span>
        </div>

        {conversationId && (
          <div className="context-item conversation-id">
            <span className="context-label">Session:</span>
            <span className="context-value">{conversationId.slice(0, 12)}...</span>
          </div>
        )}
      </div>
    </div>
  )
}

export default ConversationHeader
