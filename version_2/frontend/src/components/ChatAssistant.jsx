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

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    const messageId = addMessage('🎤 Transcribing...', 'user')
    setIsLoading(true)

    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.webm')

      const response = await fetch(`${API_BASE_URL}/voice`, {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Failed to process voice')
      }

      const transcribedText = response.headers.get('X-Transcribed-Text')
      const responseText = response.headers.get('X-Response-Text')

      if (transcribedText) {
        updateMessage(messageId, `🎤 ${transcribedText}`)
      } else {
        updateMessage(messageId, '🎤 Could not transcribe')
      }

      const audioData = await response.blob()
      const audioUrl = URL.createObjectURL(audioData)
      const audio = new Audio(audioUrl)
      audio.play()

      if (responseText) {
        addMessage(responseText, 'bot')
      } else {
        addMessage('🔊 Playing audio response...', 'bot')
      }

    } catch (error) {
      console.error('Voice error:', error)
      updateMessage(messageId, '🎤 Could not transcribe')
      addMessage('Could not process voice. Please try again.', 'bot')
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
        <div className="chat-button" onClick={() => setIsOpen(true)}>
          💬 Chat
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
            >
              {isRecording ? '⏹' : '🎤'}
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
