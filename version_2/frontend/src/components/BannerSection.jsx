import './BannerSection.css'

function BannerSection() {
  return (
    <div className="banner-section">
      <div className="banner-container">
        <div className="banner-box">
          <img 
            src="https://picsum.photos/600/300?random=1" 
            alt="Banner 1" 
            className="banner-image"
          />
        </div>
        <div className="banner-box">
          <img 
            src="https://picsum.photos/600/300?random=2" 
            alt="Banner 2" 
            className="banner-image"
          />
        </div>
      </div>
    </div>
  )
}

export default BannerSection
