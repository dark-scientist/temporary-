import BannerSection from './BannerSection'

function Settings() {
  return (
    <div style={{
      width: '100%',
      padding: '48px',
      background: 'white',
    }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{
          fontFamily: "'Sora', sans-serif",
          fontSize: '1.8rem',
          fontWeight: '700',
          color: '#00186c',
          marginBottom: '8px',
        }}>
          Settings
        </h1>
        <p style={{
          fontFamily: "'Figtree', sans-serif",
          fontSize: '0.95rem',
          color: '#888',
        }}>
          System configuration and document management
        </p>
      </div>

      <BannerSection />
    </div>
  )
}

export default Settings
