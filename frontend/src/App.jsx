import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Login from './components/Login'
import Home from './components/Home'
import Settings from './components/Settings'
import ChatAssistant from './components/ChatAssistant'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [loggedIn, setLoggedIn] = useState(false)
  const [currentUser, setCurrentUser] = useState(null)
  const [activePage, setActivePage] = useState('home')

  // Check localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('dotryder_user')
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser)
        setCurrentUser(user)
        setLoggedIn(true)
      } catch (e) {
        console.error('Failed to parse stored user:', e)
        localStorage.removeItem('dotryder_user')
      }
    }
  }, [])

  const handleLogin = async (user) => {
    // Set state
    setCurrentUser(user)
    setLoggedIn(true)
    
    // Save to localStorage
    localStorage.setItem('dotryder_user', JSON.stringify(user))
    
    // Log to backend (fire and forget)
    try {
      await fetch(`${API_BASE_URL}/log-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: user.username })
      })
    } catch (error) {
      console.error('Failed to log login:', error)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('dotryder_user')
    setLoggedIn(false)
    setCurrentUser(null)
    setActivePage('home')
  }

  // Show login screen if not logged in
  if (!loggedIn) {
    return <Login onLogin={handleLogin} />
  }

  // Main app
  return (
    <div className="app-container">
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
      
      {activePage === 'home' && (
        <Home currentUser={currentUser} setActivePage={setActivePage} />
      )}
      
      {activePage === 'settings' && <Settings />}
      
      {/* Other pages can be added here */}
      {!['home', 'settings'].includes(activePage) && (
        <div style={{
          padding: '48px',
          textAlign: 'center',
          fontFamily: "'Figtree', sans-serif",
          color: '#888',
        }}>
          <h2 style={{
            fontFamily: "'Sora', sans-serif",
            color: '#00186c',
            marginBottom: '16px',
          }}>
            {activePage.charAt(0).toUpperCase() + activePage.slice(1)}
          </h2>
          <p>This page is under construction.</p>
        </div>
      )}
      
      <ChatAssistant />
    </div>
  )
}

export default App
