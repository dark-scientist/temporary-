import { useState } from 'react'

const USERS = [
  { username: "prithwin", password: "prithwin123", displayName: "Prithwin" },
  { username: "kiran", password: "kiran123", displayName: "Kiran" },
  { username: "admin", password: "admin123", displayName: "Admin" },
]

function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    setError('')

    const user = USERS.find(
      u => u.username === username && u.password === password
    )

    if (user) {
      onLogin(user)
    } else {
      setError('Invalid username or password')
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #000009, #3533cd, #00186c)',
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '48px',
        width: '380px',
        boxShadow: '0 8px 40px rgba(0, 0, 0, 0.3)',
      }}>
        <div style={{
          width: '120px',
          height: '80px',
          background: 'linear-gradient(135deg, #000009, #3533cd)',
          borderRadius: '16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 24px auto',
          padding: '12px'
        }}>
          <img
            src="/Dot-trans.png"
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            alt="Dotryder"
          />
        </div>

        <h1 style={{
          fontFamily: "'Sora', sans-serif",
          fontSize: '1.8rem',
          fontWeight: '600',
          color: '#00186c',
          textAlign: 'center',
          marginBottom: '8px',
        }}>
          Welcome Back
        </h1>

        <p style={{
          fontFamily: "'Figtree', sans-serif",
          fontSize: '0.95rem',
          color: '#888',
          textAlign: 'center',
          marginBottom: '32px',
        }}>
          Sign in to continue
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.95rem',
                padding: '12px 16px',
                borderRadius: '10px',
                border: '1.5px solid #e0e0ea',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = '#3533cd'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0ea'}
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                fontFamily: "'Figtree', sans-serif",
                fontSize: '0.95rem',
                padding: '12px 16px',
                borderRadius: '10px',
                border: '1.5px solid #e0e0ea',
                outline: 'none',
                transition: 'border-color 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = '#3533cd'}
              onBlur={(e) => e.target.style.borderColor = '#e0e0ea'}
            />
          </div>

          {error && (
            <div style={{
              fontFamily: "'Figtree', sans-serif",
              fontSize: '0.85rem',
              color: '#cb0000',
              marginBottom: '16px',
              textAlign: 'center',
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            style={{
              width: '100%',
              fontFamily: "'Sora', sans-serif",
              fontSize: '1rem',
              fontWeight: '600',
              padding: '14px',
              borderRadius: '10px',
              border: 'none',
              background: 'linear-gradient(135deg, #3533cd, #00186c)',
              color: 'white',
              cursor: 'pointer',
              transition: 'filter 0.2s',
            }}
            onMouseEnter={(e) => e.target.style.filter = 'brightness(1.1)'}
            onMouseLeave={(e) => e.target.style.filter = 'brightness(1)'}
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
