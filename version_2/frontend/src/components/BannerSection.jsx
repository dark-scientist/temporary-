import {
  PieChart, Pie, Cell,
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  RadialBarChart, RadialBar,
  ResponsiveContainer
} from 'recharts'
import './BannerSection.css'

function BannerSection() {
  // Dummy data
  const statCards = [
    { icon: "📄", value: "5", label: "Documents", sublabel: "in knowledge base" },
    { icon: "💾", value: "12.4 MB", label: "Total Size", sublabel: "across all files" },
    { icon: "🔢", value: "347", label: "Indexed Chunks", sublabel: "vector embeddings" },
    { icon: "💬", value: "128", label: "Total Queries", sublabel: "processed so far" },
    { icon: "👥", value: "2", label: "Active Users", sublabel: "currently online" },
    { icon: "⚡", value: "2.4s", label: "Avg Response", sublabel: "per query" },
  ]

  const documentTypes = [
    { name: "PDF", value: 3, color: "#3533cd" },
    { name: "TXT", value: 2, color: "#7c96fd" },
  ]

  const queryTrend = [
    { day: "Mon", queries: 14 },
    { day: "Tue", queries: 23 },
    { day: "Wed", queries: 18 },
    { day: "Thu", queries: 31 },
    { day: "Fri", queries: 27 },
    { day: "Sat", queries: 9 },
    { day: "Sun", queries: 6 },
  ]

  const indexHealth = [{ name: "Health", value: 87, fill: "url(#healthGradient)" }]

  return (
    <>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        .stat-card {
          transition: all 0.3s ease;
        }
        .stat-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 24px rgba(0, 24, 108, 0.14) !important;
        }
      `}</style>

      <div style={{
        background: 'linear-gradient(160deg, #f8f8ff, #f0f0fa)',
        borderRadius: '20px',
        padding: '36px',
        margin: '24px 0',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '28px',
        }}>
          <h2 style={{
            fontFamily: "'Sora', sans-serif",
            fontSize: '1.5rem',
            fontWeight: '700',
            color: '#00186c',
            margin: 0,
          }}>
            System Overview
          </h2>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#22c55e',
              animation: 'pulse 2s infinite',
            }} />
            <span style={{
              fontFamily: "'Figtree', sans-serif",
              fontSize: '0.8rem',
              color: '#555',
            }}>
              Live Data
            </span>
          </div>
        </div>

        {/* Row 1: Stat Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(6, 1fr)',
          gap: '16px',
          marginBottom: '20px',
        }}>
          {statCards.map((card, index) => (
            <div
              key={index}
              className="stat-card"
              style={{
                background: 'white',
                borderRadius: '14px',
                padding: '20px 16px',
                boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <div style={{
                position: 'absolute',
                left: 0,
                top: 0,
                bottom: 0,
                width: '3px',
                background: 'linear-gradient(180deg, #3533cd, #7c96fd)',
                borderRadius: '0 3px 3px 0',
              }} />
              
              <div style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '1.8rem',
                fontWeight: '700',
                color: '#00186c',
                marginTop: '12px',
                marginBottom: '4px',
              }}>
                {card.value}
              </div>
              
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.85rem',
                fontWeight: '600',
                color: '#1a1a1a',
                marginBottom: '2px',
              }}>
                {card.label}
              </div>
              
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.75rem',
                color: '#888',
              }}>
                {card.sublabel}
              </div>
            </div>
          ))}
        </div>

        {/* Row 2: Charts */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 2fr 1fr',
          gap: '16px',
        }}>
          {/* Chart 1: Document Types Donut */}
          <div style={{
            background: 'white',
            borderRadius: '14px',
            padding: '24px',
            boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
          }}>
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '0.95rem',
                fontWeight: '700',
                color: '#00186c',
              }}>
                Document Types
              </div>
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.75rem',
                color: '#888',
                marginTop: '2px',
              }}>
                By file format
              </div>
            </div>

            <div style={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
              <PieChart width={180} height={180}>
                <defs>
                  <linearGradient id="pdfGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#3533cd" />
                    <stop offset="100%" stopColor="#00186c" />
                  </linearGradient>
                  <linearGradient id="txtGrad" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#7c96fd" />
                    <stop offset="100%" stopColor="#3533cd" />
                  </linearGradient>
                </defs>
                <Pie
                  data={documentTypes}
                  cx={90}
                  cy={90}
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  <Cell fill="url(#pdfGrad)" />
                  <Cell fill="url(#txtGrad)" />
                </Pie>
                <Tooltip />
              </PieChart>
              
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
                  5
                </div>
                <div style={{
                  fontFamily: "'Figtree', sans-serif",
                  fontSize: '0.7rem',
                  color: '#888',
                }}>
                  files
                </div>
              </div>
            </div>

            <div style={{
              display: 'flex',
              gap: '8px',
              marginTop: '16px',
              justifyContent: 'center',
            }}>
              <div style={{
                background: '#f0f0fa',
                borderRadius: '20px',
                padding: '4px 10px',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#3533cd',
                }} />
                PDF · 3
              </div>
              <div style={{
                background: '#f0f0fa',
                borderRadius: '20px',
                padding: '4px 10px',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: '#7c96fd',
                }} />
                TXT · 2
              </div>
            </div>
          </div>

          {/* Chart 2: Query Trend Line */}
          <div style={{
            background: 'white',
            borderRadius: '14px',
            padding: '24px',
            boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
          }}>
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '0.95rem',
                fontWeight: '700',
                color: '#00186c',
              }}>
                Query Trend
              </div>
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.75rem',
                color: '#888',
                marginTop: '2px',
              }}>
                Last 7 days
              </div>
            </div>

            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={queryTrend} margin={{ top: 5, right: 20, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="lineGrad" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#cb0000" />
                    <stop offset="100%" stopColor="#3533cd" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
                <XAxis
                  dataKey="day"
                  tick={{ fontFamily: 'Figtree', fontSize: 12, fill: '#888' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fontFamily: 'Figtree', fontSize: 12, fill: '#888' }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    borderRadius: '10px',
                    border: 'none',
                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                    fontFamily: 'Figtree',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="queries"
                  stroke="url(#lineGrad)"
                  strokeWidth={3}
                  dot={{ fill: '#3533cd', r: 4, strokeWidth: 0 }}
                  activeDot={{ r: 6, fill: '#cb0000' }}
                />
              </LineChart>
            </ResponsiveContainer>

            <div style={{
              display: 'flex',
              gap: '8px',
              marginTop: '12px',
              justifyContent: 'center',
            }}>
              <div style={{
                background: '#f0f0fa',
                borderRadius: '20px',
                padding: '4px 12px',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.78rem',
                color: '#555',
              }}>
                Peak: 31 queries
              </div>
              <div style={{
                background: '#f0f0fa',
                borderRadius: '20px',
                padding: '4px 12px',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.78rem',
                color: '#555',
              }}>
                Total: 128 this week
              </div>
              <div style={{
                background: '#f0f0fa',
                borderRadius: '20px',
                padding: '4px 12px',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.78rem',
                color: '#555',
              }}>
                ↑ 12% vs last week
              </div>
            </div>
          </div>

          {/* Chart 3: Index Health Gauge */}
          <div style={{
            background: 'white',
            borderRadius: '14px',
            padding: '24px',
            boxShadow: '0 2px 16px rgba(0, 24, 108, 0.08)',
          }}>
            <div style={{ marginBottom: '16px' }}>
              <div style={{
                fontFamily: "'Sora', sans-serif",
                fontSize: '0.95rem',
                fontWeight: '700',
                color: '#00186c',
              }}>
                Index Health
              </div>
              <div style={{
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.75rem',
                color: '#888',
                marginTop: '2px',
              }}>
                Vector store status
              </div>
            </div>

            <div style={{ position: 'relative', display: 'flex', justifyContent: 'center' }}>
              <RadialBarChart
                width={180}
                height={180}
                innerRadius={50}
                outerRadius={80}
                startAngle={220}
                endAngle={-40}
                data={indexHealth}
              >
                <defs>
                  <linearGradient id="healthGradient" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#3533cd" />
                    <stop offset="100%" stopColor="#7c96fd" />
                  </linearGradient>
                </defs>
                <RadialBar
                  dataKey="value"
                  cornerRadius={8}
                  background={{ fill: '#f0f0fa' }}
                />
                <Tooltip />
              </RadialBarChart>

              <div style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
              }}>
                <div style={{
                  fontFamily: "'Sora', sans-serif",
                  fontSize: '1.6rem',
                  fontWeight: '700',
                  color: '#00186c',
                }}>
                  87%
                </div>
                <div style={{
                  fontFamily: "'Figtree', sans-serif",
                  fontSize: '0.75rem',
                  color: '#22c55e',
                }}>
                  Healthy
                </div>
              </div>
            </div>

            <div style={{
              marginTop: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px',
            }}>
              {['Index loaded', '347 chunks ready', 'Embeddings active'].map((text, i) => (
                <div key={i} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}>
                  <div style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: '#22c55e',
                  }} />
                  <span style={{
                    fontFamily: "'Figtree', sans-serif",
                    fontSize: '0.8rem',
                    color: '#555',
                  }}>
                    ✓ {text}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default BannerSection
