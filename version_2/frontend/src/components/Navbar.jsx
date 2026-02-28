import React from 'react'
import './Navbar.css'

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-left">
        <div className="logo">Dotryder</div>
      </div>
      
      <div className="navbar-center">
        <a href="#home" className="nav-link">Home</a>
        <a href="#about" className="nav-link">About</a>
        <a href="#services" className="nav-link">Services</a>
        <a href="#contact" className="nav-link">Contact</a>
        <a href="#solutions" className="nav-link">Solutions</a>
      </div>
      
      <div className="navbar-right">
        <div className="user-profile">
          <div className="avatar">U</div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
