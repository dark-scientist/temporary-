import { useState, useEffect, useRef } from 'react'
import './ChatAssistant.css'

const API_BASE_URL = 'http://localhost:8000'

function ChatAssistant() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [backendStatus, setBackendStatus] = useState('checking')
  const [mediaRecorder, setMediaRecorder] = useState(null)
  const [audioContext, setAudioContext] = useState(null)
  const [messageIdCounter, setMessageIdCounter] = useState(0)
  const [isHovered, setIsHovered] = useState(false)
  
  const messagesEndRef = useRef(null)
  const recordingTimeoutRef = useRef(null)

  useEffect(() => {
    checkBackendHealth()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      addMessage(
        "Hi! I'm the Document Bot. Ask me anything about your documents, or use the mic to speak your question.",
        'bot'
      )
    }
  }, [isOpen])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkBackendHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      if (response.ok) {
        const data = await response.json()
        setBackendStatus(data.index_loaded ? 'online' : 'no-index')
      } else {
        setBackendStatus('offline')
      }
    } catch (error) {
      setBackendStatus('offline')
    }
  }

  const addMessage = (text, sender, timestamp = new Date()) => {
    const id = messageIdCounter
    setMessageIdCounter(prev => prev + 1)
    setMessages(prev => [...prev, { id, text, sender, timestamp }])
    return id
  }

  const updateMessage = (id, newText) => {
    setMessages(prev => 
      prev.map(msg => msg.id === id ? { ...msg, text: newText } : msg)
    )
  }

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return

    const userMessage = inputText.trim()
    setInputText('')
    addMessage(userMessage, 'user')
    setIsLoading(true)

    // Get current user from localStorage
    const currentUser = JSON.parse(localStorage.getItem('dotryder_user') || '{}')
    const username = currentUser.username || 'anonymous'

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-Username': username
        },
        body: JSON.stringify({
          message: userMessage
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      addMessage(data.response, 'bot')
    } catch (error) {
      console.error('Chat error:', error)
      addMessage('Sorry, something went wrong. Is the backend running?', 'bot')
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const detectSilence = (stream, onSilence) => {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const analyser = audioCtx.createAnalyser()
    const microphone = audioCtx.createMediaStreamSource(stream)
    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    microphone.connect(analyser)
    analyser.fftSize = 2048

    let silenceStart = Date.now()
    const SILENCE_THRESHOLD = 10
    const SILENCE_DURATION = 3000

    const checkAudioLevel = () => {
      analyser.getByteTimeDomainData(dataArray)
      
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        sum += Math.abs(dataArray[i] - 128)
      }
      const average = sum / dataArray.length

      if (average < SILENCE_THRESHOLD) {
        if (Date.now() - silenceStart > SILENCE_DURATION) {
          onSilence()
          return
        }
      } else {
        silenceStart = Date.now()
      }

      if (mediaRecorder && mediaRecorder.state === 'recording') {
        requestAnimationFrame(checkAudioLevel)
      }
    }

    setAudioContext(audioCtx)
    checkAudioLevel()
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { 
        mimeType: 'audio/webm;codecs=opus' 
      })
      
      const chunks = []
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data)
        }
      }

      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' })
        await sendVoiceMessage(audioBlob)
        stream.getTracks().forEach(track => track.stop())
        if (audioContext) {
          audioContext.close()
        }
      }

      recorder.start()
      setMediaRecorder(recorder)
      setIsRecording(true)

      detectSilence(stream, () => {
        stopRecording()
      })

      recordingTimeoutRef.current = setTimeout(() => {
        stopRecording()
      }, 10000)

    } catch (error) {
      console.error('Recording error:', error)
      addMessage('Could not access microphone. Please check permissions.', 'bot')
    }
  }

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
      setIsRecording(false)
      if (recordingTimeoutRef.current) {
        clearTimeout(recordingTimeoutRef.current)
      }
    }
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const sendVoiceMessage = async (audioBlob) => {
    const messageId = addMessage('Transcribing...', 'user')
    setIsLoading(true)

    // Get current user from localStorage
    const currentUser = JSON.parse(localStorage.getItem('dotryder_user') || '{}')
    const username = currentUser.username || 'anonymous'

    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')

      const response = await fetch(`${API_BASE_URL}/voice`, {
        method: 'POST',
        headers: {
          'X-Username': username
        },
        body: formData
      })

      if (!response.ok) {
        let detail = 'Failed to process voice'
        try {
          const errorBody = await response.json()
          detail = errorBody?.detail || detail
        } catch (_) {
          // Ignore JSON parse errors and use fallback detail.
        }
        throw new Error(detail)
      }

      const decodeB64Utf8 = (value) => {
        if (!value) return null
        try {
          const binary = atob(value)
          const bytes = Uint8Array.from(binary, char => char.charCodeAt(0))
          return new TextDecoder().decode(bytes)
        } catch (_) {
          return null
        }
      }

      const transcribedText = (
        decodeB64Utf8(response.headers.get('X-Transcribed-Text-B64')) ||
        response.headers.get('X-Transcribed-Text')
      )
      const responseText = (
        decodeB64Utf8(response.headers.get('X-Response-Text-B64')) ||
        response.headers.get('X-Response-Text')
      )

      if (transcribedText) {
        updateMessage(messageId, transcribedText)
      } else {
        updateMessage(messageId, 'Could not transcribe')
      }

      const audioData = await response.blob()
      const audioUrl = URL.createObjectURL(audioData)
      const audio = new Audio(audioUrl)
      audio.play()

      if (responseText) {
        addMessage(responseText, 'bot')
      } else {
        addMessage('Playing audio response...', 'bot')
      }

    } catch (error) {
      console.error('Voice error:', error)
      updateMessage(messageId, 'Could not transcribe')
      addMessage(error.message || 'Could not process voice. Please try again.', 'bot')
    } finally {
      setIsLoading(false)
    }
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <>
      {!isOpen && (
        <div 
          style={{
            position: 'fixed',
            bottom: '24px',
            right: '24px',
            width: '60px',
            height: '60px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #000009, #3533cd, #00186c)',
            boxShadow: '0 4px 24px rgba(53, 51, 205, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'transform 0.2s',
            transform: isHovered ? 'scale(1.08)' : 'scale(1)',
            zIndex: 1000,
          }}
          onClick={() => setIsOpen(true)}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <img 
            src="/Dot-trans.png" 
            alt="Chat"
            style={{ 
              width: '38px', 
              height: '38px', 
              objectFit: 'contain' 
            }}
          />
          {isHovered && (
            <div style={{
              position: 'absolute',
              bottom: '70px',
              left: '50%',
              transform: 'translateX(-50%)',
              background: '#1a1a1a',
              color: 'white',
              padding: '4px 12px',
              borderRadius: '20px',
              fontFamily: "'Figtree', sans-serif",
              fontSize: '0.8rem',
              whiteSpace: 'nowrap',
            }}>
              Chat
            </div>
          )}
        </div>
      )}

      {isOpen && (
        <div className="chat-panel">
          <div className="chat-header">
            <span className="chat-title">Document Bot</span>
            <button className="close-button" onClick={() => setIsOpen(false)}>
              ✕
            </button>
          </div>

          {backendStatus === 'offline' && (
            <div className="status-warning offline">
              ⚠ Backend offline. Start the API first.
            </div>
          )}
          {backendStatus === 'no-index' && (
            <div className="status-warning no-index">
              ⚠ No index found — please run build_index.py first
            </div>
          )}

          <div className="messages-area">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}-message`}>
                <div className="message-bubble">
                  {msg.text}
                </div>
                <div className="message-time">
                  {formatTime(msg.timestamp)}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message bot-message">
                <div className="message-bubble typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              className="message-input"
              placeholder={isRecording ? "Recording..." : "Type your question..."}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading || isRecording}
            />
            <button
              className={`mic-button ${isRecording ? 'recording' : ''}`}
              onClick={toggleRecording}
              disabled={isLoading}
              title={isRecording ? 'Stop recording' : 'Start recording'}
              style={{
                background: isRecording ? '#cb0000' : '#e0e0ea',
                color: isRecording ? 'white' : '#0a0a0a',
              }}
            >
              <svg 
                width="18" 
                height="18" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>
            <button
              className="send-button"
              onClick={handleSendMessage}
              disabled={isLoading || !inputText.trim() || isRecording}
            >
              Send
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default ChatAssistant
