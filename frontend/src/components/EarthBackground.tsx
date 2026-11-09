import { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'

interface EarthBackgroundProps {
  /** Test override for reduced motion fallback simulation */
  forceReducedMotion?: boolean
  /** Test override for WebGL unavailability fallback simulation */
  forceDisableWebGL?: boolean
}

export default function EarthBackground({
  forceReducedMotion = false,
  forceDisableWebGL = false,
}: EarthBackgroundProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [useFallback, setUseFallback] = useState(false)

  useEffect(() => {
    // Check prefers-reduced-motion media query
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    const prefersReducedMotion = forceReducedMotion || mediaQuery.matches

    // Check WebGL availability
    const checkWebGL = (): boolean => {
      if (forceDisableWebGL) return false
      try {
        const canvas = document.createElement('canvas')
        return !!(
          window.WebGLRenderingContext &&
          (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
        )
      } catch {
        return false
      }
    }

    const hasWebGL = checkWebGL()

    if (prefersReducedMotion || !hasWebGL) {
      setUseFallback(true)
      return
    }

    const container = containerRef.current
    if (!container) return

    // Scene & Camera setup
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    )
    camera.position.z = 2.4

    // Renderer setup (capped at 1.5 devicePixelRatio)
    let renderer: THREE.WebGLRenderer
    try {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5))
      renderer.setSize(window.innerWidth, window.innerHeight)
      renderer.outputColorSpace = THREE.SRGBColorSpace
      container.appendChild(renderer.domElement)
    } catch {
      setUseFallback(true)
      return
    }

    // Geometry & Texture loading (from local /textures/ only, never CDN)
    const textureLoader = new THREE.TextureLoader()
    const earthTexture = textureLoader.load(
      '/textures/earth_atmos_2048.jpg',
      () => renderer.render(scene, camera),
      undefined,
      () => setUseFallback(true)
    )

    const geometry = new THREE.SphereGeometry(0.85, 48, 48)
    const material = new THREE.MeshPhongMaterial({
      map: earthTexture,
      shininess: 12,
      specular: new THREE.Color(0x1e3a8a),
    })
    const globe = new THREE.Mesh(geometry, material)
    globe.rotation.y = 0.5
    globe.rotation.x = 0.2
    scene.add(globe)

    // Directional lighting to simulate sun angle + soft ambient
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.45)
    scene.add(ambientLight)

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.6)
    sunLight.position.set(3, 1.5, 3)
    scene.add(sunLight)

    // Rotation calculation: 1 full rotation (2 * PI) every 120 seconds
    const rotationSpeedPerSecond = (2 * Math.PI) / 120
    let lastTime = performance.now()
    let animationFrameId: number
    let isPaused = document.hidden

    const animate = (currentTime: number) => {
      const delta = (currentTime - lastTime) / 1000
      lastTime = currentTime

      if (!isPaused) {
        globe.rotation.y += rotationSpeedPerSecond * delta
        renderer.render(scene, camera)
      }
      animationFrameId = requestAnimationFrame(animate)
    }

    animationFrameId = requestAnimationFrame(animate)

    // Pause rendering when tab/document is hidden
    const handleVisibilityChange = () => {
      isPaused = document.hidden
      if (!isPaused) {
        lastTime = performance.now()
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)

    // Window resize handler
    const handleResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }
    window.addEventListener('resize', handleResize)

    return () => {
      cancelAnimationFrame(animationFrameId)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('resize', handleResize)
      if (renderer.domElement && container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
      geometry.dispose()
      material.dispose()
      earthTexture.dispose()
      renderer.dispose()
    }
  }, [forceReducedMotion, forceDisableWebGL])

  return (
    <div
      aria-hidden="true"
      data-testid="earth-background-container"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      {/* 3D Canvas / Three.js Container */}
      <div
        ref={containerRef}
        data-testid="three-canvas-wrapper"
        style={{
          width: '100%',
          height: '100%',
          opacity: 0.35,
          display: useFallback ? 'none' : 'block',
        }}
      />

      {/* Static Image / Reduced Motion Fallback */}
      {useFallback && (
        <div
          data-testid="earth-static-fallback"
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            opacity: 0.35,
            backgroundImage: 'url(/textures/earth_atmos_2048.jpg)',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            filter: 'brightness(0.6) saturate(0.8)',
          }}
        />
      )}

      {/* Dark gradient overlay so text never sits on bright Earth areas */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background:
            'radial-gradient(circle at 60% 40%, rgba(7, 11, 20, 0.55) 0%, rgba(3, 7, 18, 0.94) 80%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  )
}

