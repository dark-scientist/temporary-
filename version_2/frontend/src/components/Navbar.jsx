import './Navbar.css'

function Navbar({ activePage, setActivePage, currentUser, onLogout }) {
  const navLinks = ['home', 'about', 'services', 'contact', 'solutions', 'settings']

  const getInitials = (name) => {
    return name ? name.charAt(0).toUpperCase() : 'U'
  }

  return (
    <nav className="navbar">
      <div className="navbar-left">
        <img src="/Dot-trans.png" alt="Dotryder" className="logo-image" />
      </div>
      
      <div className="navbar-center">
        {navLinks.map((link) => (
          <a
            key={link}
            href={`#${link}`}
            className={`nav-link ${activePage === link ? 'active' : ''}`}
            onClick={(e) => {
              e.preventDefault()
              setActivePage(link)
            }}
            style={{
              color: activePage === link ? '#cb0000' : '#00186c',
              fontWeight: activePage === link ? '600' : '400',
            }}
          >
            {link.charAt(0).toUpperCase() + link.slice(1)}
          </a>
        ))}
      </div>
      
      <div className="navbar-right">
        <button
          onClick={onLogout}
          style={{
            fontFamily: "'Figtree', sans-serif",
            fontSize: '0.9rem',
            color: '#cb0000',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            marginRight: '16px',
            transition: 'text-decoration 0.2s',
          }}
          onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
          onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
        >
          Logout
        </button>
        <div className="user-profile">
          <div className="avatar">{getInitials(currentUser?.displayName)}</div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
