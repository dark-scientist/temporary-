import React from 'react'
import './DocumentBotSection.css'

function DocumentBotSection() {
  return (
    <div className="document-bot-section">
      <div className="document-bot-container">
        <div className="image-placeholder">
          <img 
            src="https://picsum.photos/300/250?random=3" 
            alt="Document Bot" 
            className="placeholder-image"
          />
        </div>
        <div className="content-area">
          <h2 className="section-title">Document Bot</h2>
          <p className="section-description">
            A unified RAG-powered conversational assistant that seamlessly handles 
            multilingual documents can greatly enhance productivity by combining 
            translation, insight extraction, and natural dialogue.
          </p>
        </div>
      </div>
    </div>
  )
}

export default DocumentBotSection
