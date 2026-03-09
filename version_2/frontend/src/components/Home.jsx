import { useState, useEffect } from 'react'
import {
  PieChart, Pie, Cell,
  RadialBarChart, RadialBar,
  Tooltip, ResponsiveContainer
} from 'recharts'

const API_BASE_URL = 'http://localhost:8000'

function Home({ currentUser, setActivePage }) {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [chatHistory, setChatHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  // Fallback dummy data
  const fallbackStats = {
    totalDocuments: 5,
    totalSizeMB: 12.4,
    totalChunks: 347,
    totalQueries: 128,
    activeUsers: 2,
    avgResponseTime: 3.8,
    documentTypes: [
      { name: "PDF", value: 3, color: "#3533cd" },
      { name: "TXT", value: 2, color: "#7c96fd" },
    ],
    documentDomains: [
      { name: "HR", value: 2, color: "#cb0000" },
      { name: "Legal", value: 1, color: "#3533cd" },
      { name: "Finance", value: 1, color: "#7c96fd" },
      { name: "General", value: 1, color: "#00186c" },
    ]
  }

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    fetchStats()
    fetchChatHistory()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`)
      if (response.ok) {
        const data = await response.json()
        // Add dummy domain data since backend doesn't provide it yet
        data.documentDomains = fallbackStats.documentDomains
        setStats(data)
      } else {
        setStats(fallbackStats)
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      setStats(fallbackStats)
    } finally {
      setStatsLoading(false)
    }
  }

  const fetchChatHistory = async () => {
    setHistoryLoading(true)
    try {
      const response = await fetch(
        `${API_BASE_URL}/chat-history?username=${currentUser.username}`
      )
      if (response.ok) {
        const data = await response.json()
        setChatHistory(data.history || [])
      } else {
        setChatHistory([])
      }
    } catch (error) {
      console.error('Failed to fetch chat history:', error)
      setChatHistory([])
    } finally {
      setHistoryLoading(false)
    }
  }

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchChatHistory()
    setTimeout(() => setRefreshing(false), 500)
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const timeAgo = (timestamp) => {
    const now = new Date()
    const past = new Date(timestamp)
    const diffMs = now - past
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    return past.toLocaleDateString()
  }

  const truncateText = (text, maxLength) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
  }

  const displayStats = stats || fallbackStats

  return (
    <>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        .skeleton {
          animation: pulse 1.5s ease-in-out infinite;
          background: #f0f0f0;
          border-radius: 8px;
        }
      `}</style>

      <div style={{
        width: '100%',
        padding: '36px',
        background: 'white',
      }}>
        {/* Welcome Bar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingBottom: '20px',
          marginBottom: '28px',
          borderBottom: '1px solid #f0f0f0',
        }}>
          <div>
            <h1 style={{
              fontFamily: "'Sora', sans-serif",
              fontSize: '2rem',
              fontWeight: '700',
              color: '#00186c',
              marginBottom: '6px',
            }}>
              Hello, {currentUser.displayName}! 👋
            </h1>
            <p style={{
              fontFamily: "'Figtree', sans-serif",
              fontSize: '1rem',
              color: '#888',
            }}>
              Here's your document intelligence overview
            </p>
          </div>

          <div style={{
            fontFamily: "'Figtree', sans-serif",
            fontSize: '0.9rem',
            color: '#555',
            textAlign: 'right',
          }}>
            <div>{formatDate(currentTime)}</div>
            <div style={{ marginTop: '4px', fontWeight: '600' }}>
              {formatTime(currentTime)}
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '65% 35%',
          gap: '24px',
        }}>
          {/* LEFT COLUMN - Charts */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}>
            {/* Chart 1 - Domain Categories Donut */}
            <div style={{
              background: 'white',
              borderRadius: '14px',
              padding: '24px',
              boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
            }}>
              <h3 style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '1rem',
                fontWeight: '700',
                color: '#00186c',
                marginBottom: '4px',
              }}>
                Domain
              </h3>
              <p style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.8rem',
                color: '#888',
                marginBottom: '16px',
              }}>
                Auto-identified by content
              </p>

              {statsLoading ? (
                <div className="skeleton" style={{ height: '200px', width: '200px', margin: '0 auto' }} />
              ) : (
                <div style={{ position: 'relative', width: '200px', height: '200px', margin: '0 auto' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={displayStats.documentDomains}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {displayStats.documentDomains.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center',
                  }}>
                    <div style={{
                      fontFamily: "'Sora', sans-serif",
                      fontSize: '1.8rem',
                      fontWeight: '700',
                      color: '#00186c',
                    }}>
                      {displayStats.documentDomains.length}
                    </div>
                    <div style={{
                      fontFamily: "'Figtree', sans-serif",
                      fontSize: '0.75rem',
                      color: '#888',
                    }}>
                      domains
                    </div>
                  </div>
                </div>
              )}

              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '8px',
                marginTop: '16px',
                justifyItems: 'center',
              }}>
                {displayStats.documentDomains.map((domain, idx) => (
                  <div key={idx} style={{
                    background: '#f0f0fa',
                    borderRadius: '20px',
                    padding: '4px 12px',
                    fontFamily: "'Figtree', sans-serif",
                    fontSize: '0.78rem',
                    color: '#555',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: domain.color,
                    }} />
                    {domain.name} · {domain.value}
                  </div>
                ))}
              </div>
            </div>

            {/* Chart 2 - Document Types Donut */}
            <div style={{
              background: 'white',
              borderRadius: '14px',
              padding: '24px',
              boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
            }}>
              <h3 style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '1rem',
                fontWeight: '700',
                color: '#00186c',
                marginBottom: '4px',
              }}>
                Type
              </h3>
              <p style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.8rem',
                color: '#888',
                marginBottom: '16px',
              }}>
                By file format
              </p>

              {statsLoading ? (
                <div className="skeleton" style={{ height: '200px', width: '200px', margin: '0 auto' }} />
              ) : (
                <div style={{ position: 'relative', width: '200px', height: '200px', margin: '0 auto' }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <defs>
                        <linearGradient id="pdfGradient" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0%" stopColor="#3533cd" />
                          <stop offset="100%" stopColor="#00186c" />
                        </linearGradient>
                        <linearGradient id="txtGradient" x1="0" y1="0" x2="1" y2="1">
                          <stop offset="0%" stopColor="#7c96fd" />
                          <stop offset="100%" stopColor="#3533cd" />
                        </linearGradient>
                      </defs>
                      <Pie
                        data={displayStats.documentTypes}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {displayStats.documentTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={index === 0 ? 'url(#pdfGradient)' : 'url(#txtGradient)'} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center',
                  }}>
                    <div style={{
                      fontFamily: "'Sora', sans-serif",
                      fontSize: '1.8rem',
                      fontWeight: '700',
                      color: '#00186c',
                    }}>
                      {displayStats.totalDocuments}
                    </div>
                    <div style={{
                      fontFamily: "'Figtree', sans-serif",
                      fontSize: '0.75rem',
                      color: '#888',
                    }}>
                      files
                    </div>
                  </div>
                </div>
              )}

              <div style={{
                display: 'flex',
                justifyContent: 'center',
                gap: '16px',
                marginTop: '16px',
              }}>
                {displayStats.documentTypes.map((type, idx) => (
                  <div key={idx} style={{
                    background: '#f0f0fa',
                    borderRadius: '20px',
                    padding: '4px 12px',
                    fontFamily: "'Figtree', sans-serif",
                    fontSize: '0.78rem',
                    color: '#555',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}>
                    <div style={{
                      width: '8px',
                      height: '8px',
                      borderRadius: '50%',
                      background: type.color,
                    }} />
                    {type.name} · {type.value}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN - Chat History */}
          <div style={{
            background: 'white',
            borderRadius: '14px',
            padding: '24px',
            boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
            display: 'flex',
            flexDirection: 'column',
            overflowY: 'auto',
            maxHeight: '85vh',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '16px',
            }}>
              <div>
                <h3 style={{
                  fontFamily: "'Sora', sans-serif",
                  fontSize: '1rem',
                  fontWeight: '700',
                  color: '#00186c',
                  marginBottom: '4px',
                }}>
                  Recent Activity
                </h3>
                <p style={{
                  fontFamily: "'Figtree', sans-serif",
                  fontSize: '0.8rem',
                  color: '#888',
                }}>
                  Your previous queries
                </p>
              </div>
              <button
                onClick={handleRefresh}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#3533cd',
                  fontSize: '1.2rem',
                  cursor: 'pointer',
                  transition: 'transform 0.3s',
                  transform: refreshing ? 'rotate(180deg)' : 'rotate(0deg)',
                }}
              >
                🔄
              </button>
            </div>

            <div style={{
              flex: 1,
              overflowY: 'auto',
            }}>
              {historyLoading ? (
                <>
                  {[1, 2, 3].map(i => (
                    <div key={i} className="skeleton" style={{
                      height: '80px',
                      marginBottom: '10px',
                    }} />
                  ))}
                </>
              ) : chatHistory.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  padding: '40px 20px',
                  fontFamily: "'Figtree', sans-serif",
                  color: '#888',
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '12px' }}>💬</div>
                  <div>No queries yet. Start chatting to see your history here.</div>
                </div>
              ) : (
                chatHistory.map((item) => (
                  <div
                    key={item.id}
                    style={{
                      background: '#f8f8ff',
                      borderRadius: '10px',
                      padding: '12px 14px',
                      marginBottom: '10px',
                      borderLeft: '3px solid #3533cd',
                      transition: 'all 0.2s',
                      cursor: 'default',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = '#f0f0fa'
                      e.currentTarget.style.borderLeftColor = '#cb0000'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = '#f8f8ff'
                      e.currentTarget.style.borderLeftColor = '#3533cd'
                    }}
                  >
                    <div style={{
                      fontFamily: "'Figtree', sans-serif",
                      fontSize: '0.88rem',
                      fontWeight: '600',
                      color: '#1a1a1a',
                      marginBottom: '6px',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}>
                      🔍 {item.question}
                    </div>
                    <div style={{
                      fontFamily: "'Figtree', sans-serif",
                      fontSize: '0.8rem',
                      color: '#666',
                      marginBottom: '6px',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                    }}>
                      {item.response}
                    </div>
                    <div style={{
                      fontFamily: "'Figtree', sans-serif",
                      fontSize: '0.72rem',
                      color: '#aaa',
                      textAlign: 'right',
                    }}>
                      {timeAgo(item.timestamp)}
                    </div>
                  </div>
                ))
              )}
            </div>

            {chatHistory.length > 0 && (
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.75rem',
                color: '#aaa',
                textAlign: 'center',
                marginTop: '12px',
                paddingTop: '12px',
                borderTop: '1px solid #f0f0f0',
              }}>
                Showing all saved queries ({chatHistory.length})
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  )
}

export default Home
