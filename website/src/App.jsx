import { useEffect } from 'react'
import Nav from './components/Nav'
import Hero from './components/Hero'
import TUIPreview from './components/TUIPreview'
import Features from './components/Features'
import KeyBindings from './components/KeyBindings'
import Security from './components/Security'
import TechStack from './components/TechStack'
import Install from './components/Install'
import Footer from './components/Footer'

function App() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add('visible')
        })
      },
      { threshold: 0.1, rootMargin: '0px 0px -60px 0px' }
    )
    document.querySelectorAll('.reveal').forEach((el) => observer.observe(el))
    return () => observer.disconnect()
  }, [])

  return (
    <div className="relative">
      <Nav />
      <Hero />
      <TUIPreview />
      <Features />
      <KeyBindings />
      <Security />
      <TechStack />
      <Install />
      <Footer />
    </div>
  )
}

export default App
