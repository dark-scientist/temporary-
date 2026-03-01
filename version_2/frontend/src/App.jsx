import Navbar from './components/Navbar'
import BannerSection from './components/BannerSection'
import DocumentBotSection from './components/DocumentBotSection'
import ChatAssistant from './components/ChatAssistant'
import './App.css'

function App() {
  return (
    <div className="app-container">
      <Navbar />
      <BannerSection />
      <DocumentBotSection />
      <ChatAssistant />
    </div>
  )
}

export default App
