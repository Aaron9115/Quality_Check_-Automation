import { useEffect, useRef, useState } from 'react'
import { motion, useAnimation, useInView } from 'framer-motion'
import './LandingPage.css'

function LandingPage({ onNavigate }) {
  const canvasRef = useRef(null)
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })
  const featuresRef = useRef(null)
  const isInView = useInView(featuresRef, { once: true, amount: 0.2 })
  const controls = useAnimation()

  // Mouse tracking for parallax
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePos({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20
      })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Particle Canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    let width = window.innerWidth
    let height = window.innerHeight
    let particles = []
    let animationId = null

    const resize = () => {
      width = window.innerWidth
      height = window.innerHeight
      canvas.width = width
      canvas.height = height
    }

    window.addEventListener('resize', resize)
    resize()

    class Particle {
      constructor() {
        this.x = Math.random() * width
        this.y = Math.random() * height
        this.size = Math.random() * 2.5 + 0.5
        this.speedX = (Math.random() - 0.5) * 0.2
        this.speedY = (Math.random() - 0.5) * 0.2
        this.opacity = Math.random() * 0.2 + 0.05
        this.originalX = this.x
        this.originalY = this.y
        this.pulse = Math.random() * Math.PI * 2
      }

      update(mouseX, mouseY) {
        const dx = this.x - mouseX
        const dy = this.y - mouseY
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 200) {
          const force = (200 - dist) / 200 * 0.5
          this.x += (dx / dist) * force
          this.y += (dy / dist) * force
        } else {
          this.x += (this.originalX - this.x) * 0.01
          this.y += (this.originalY - this.y) * 0.01
        }
        this.pulse += 0.02
        this.size = 1.5 + Math.sin(this.pulse) * 0.8
      }

      draw() {
        ctx.beginPath()
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(236, 186, 148, ${this.opacity + Math.sin(this.pulse) * 0.05})`
        ctx.fill()
      }
    }

    const numParticles = Math.min(50, Math.floor((width * height) / 25000))
    for (let i = 0; i < numParticles; i++) {
      particles.push(new Particle())
    }

    const drawLines = () => {
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x
          const dy = particles[i].y - particles[j].y
          const distance = Math.sqrt(dx * dx + dy * dy)

          if (distance < 180) {
            const opacity = (1 - distance / 180) * 0.06
            ctx.beginPath()
            ctx.moveTo(particles[i].x, particles[i].y)
            ctx.lineTo(particles[j].x, particles[j].y)
            ctx.strokeStyle = `rgba(236, 186, 148, ${opacity})`
            ctx.lineWidth = 0.3
            ctx.stroke()
          }
        }
      }
    }

    const animate = () => {
      ctx.clearRect(0, 0, width, height)
      const centerX = width / 2 + mousePos.x * 5
      const centerY = height / 2 + mousePos.y * 5
      particles.forEach(p => {
        p.update(centerX, centerY)
        p.draw()
      })
      drawLines()
      animationId = requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener('resize', resize)
      if (animationId) cancelAnimationFrame(animationId)
    }
  }, [mousePos])

  // Stagger children animation
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] }
    }
  }

  const featureCardVariants = {
    hidden: { opacity: 0, y: 40, scale: 0.95 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] }
    },
    hover: {
      y: -12,
      scale: 1.02,
      transition: { duration: 0.3 }
    }
  }

  return (
    <div className="landing-page">
      <canvas ref={canvasRef} className="particle-canvas" />
      
      {/* Mouse-Follow Glow */}
      <div 
        className="mouse-glow"
        style={{
          left: mousePos.x * 5 + 'px',
          top: mousePos.y * 5 + 'px'
        }}
      ></div>

      {/* Decorative Elements */}
      <div className="deco-ring ring-1" style={{ transform: `translate(${mousePos.x * 0.3}px, ${mousePos.y * 0.3}px)` }}></div>
      <div className="deco-ring ring-2" style={{ transform: `translate(${-mousePos.x * 0.2}px, ${-mousePos.y * 0.2}px)` }}></div>
      <div className="deco-ring ring-3" style={{ transform: `translate(${mousePos.x * 0.1}px, ${mousePos.y * 0.1}px)` }}></div>

      <div className="bg-glow glow-left"></div>
      <div className="bg-glow glow-right"></div>

      {/* HERO SECTION */}
      <section className="hero-section">
        <motion.div 
          className="hero-content"
          initial="hidden"
          animate="visible"
          variants={containerVariants}
        >
          <motion.div variants={itemVariants} className="hero-badge">
            <span className="badge-icon">✦</span>
            British English QC
            <span className="badge-pulse-ring"></span>
          </motion.div>
          
          <motion.h1 variants={itemVariants} className="hero-title">
            Quality Control
            <span className="hero-highlight">Reimagined</span>
          </motion.h1>
          
          <motion.p variants={itemVariants} className="hero-description">
            A refined approach to grammar, spelling, and logic checking.
            Ensuring your content meets British English standards with precision.
          </motion.p>
          
          <motion.div variants={itemVariants} className="hero-actions">
            <button className="hero-btn primary" onClick={() => onNavigate('text')}>
              <span>Get Started</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M12 5L19 12L12 19" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <span className="btn-shimmer"></span>
            </button>
            <button className="hero-btn secondary" onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}>
              Discover
            </button>
          </motion.div>
        </motion.div>

        <motion.div 
          className="hero-stats"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <div className="stat-item">
            <span className="stat-number">3</span>
            <span className="stat-label">Features</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">100%</span>
            <span className="stat-label">British English</span>
          </div>
          <div className="stat-divider"></div>
          <div className="stat-item">
            <span className="stat-number">AI</span>
            <span className="stat-label">Powered</span>
          </div>
        </motion.div>

        <div className="scroll-indicator">
          <span>Scroll</span>
          <div className="scroll-line"></div>
        </div>
      </section>

      {/* FEATURES SECTION - FIXED VERTICAL STACKING */}
      <section id="features" className="features-section" ref={featuresRef}>
        <div className="section-header">
          <span className="section-tag">Capabilities</span>
          <h2>Three Core Tools</h2>
          <p>Designed for clarity, precision, and efficiency</p>
        </div>

        <motion.div 
          className="features-grid"
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          variants={containerVariants}
        >
          <motion.div 
            className="feature-card" 
            onClick={() => onNavigate('text')}
            variants={featureCardVariants}
            whileHover="hover"
          >
            <div className="feature-number">01</div>
            <div className="feature-icon text-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M4 7H20" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 12H20" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M4 17H14" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </div>
            <h3>Text Check</h3>
            <p>Grammar, spelling, and logic analysis with British English standards.</p>
            <span className="feature-arrow">→</span>
            <div className="feature-hover-glow"></div>
          </motion.div>

          <motion.div 
            className="feature-card" 
            onClick={() => onNavigate('image')}
            variants={featureCardVariants}
            whileHover="hover"
          >
            <div className="feature-number">02</div>
            <div className="feature-icon image-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="3" width="20" height="18" rx="3" stroke="currentColor" strokeWidth="1.5"/>
                <circle cx="8.5" cy="8.5" r="2.5" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M21 15L16 10L5 21" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </div>
            <h3>Image Alignment</h3>
            <p>Detect logo overlaps and alignment issues in visual assets.</p>
            <span className="feature-arrow">→</span>
            <div className="feature-hover-glow"></div>
          </motion.div>

          <motion.div 
            className="feature-card" 
            onClick={() => onNavigate('pdf')}
            variants={featureCardVariants}
            whileHover="hover"
          >
            <div className="feature-number">03</div>
            <div className="feature-icon pdf-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="1.5"/>
                <path d="M14 2V8H20" stroke="currentColor" strokeWidth="1.5"/>
              </svg>
            </div>
            <h3>PDF QC</h3>
            <p>Comprehensive document QC with page tracking and TOC validation.</p>
            <span className="feature-arrow">→</span>
            <div className="feature-hover-glow"></div>
          </motion.div>
        </motion.div>
      </section>

      {/* FOOTER */}
      <footer className="landing-footer">
        <div className="footer-content">
          <motion.span 
            className="footer-brand"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            ◈ British English QC
          </motion.span>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9 }}
          >
            © 2026
          </motion.p>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage