import '@testing-library/jest-dom/vitest'
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SyntheticBanner from '../components/SyntheticBanner'
import EarthBackground from '../components/EarthBackground'

describe('SyntheticBanner Component', () => {
  it('renders disclosure text and role alert', () => {
    render(<SyntheticBanner />)
    const banner = screen.getByRole('alert')
    expect(banner).toBeInTheDocument()
    expect(banner).toHaveTextContent(
      'SYNTHETIC DATA MODE ACTIVE — Results on synthetic data demonstrate the method, not real-world accuracy.'
    )
  })

  it('has accessible label', () => {
    render(<SyntheticBanner />)
    expect(
      screen.getByLabelText('Synthetic Simulation Data Disclosure')
    ).toBeInTheDocument()
  })
})

describe('EarthBackground Component', () => {
  it('renders static fallback when prefers-reduced-motion is active', () => {
    render(<EarthBackground forceReducedMotion={true} />)
    const fallback = screen.getByTestId('earth-static-fallback')
    expect(fallback).toBeInTheDocument()
    expect(fallback).toHaveStyle({
      backgroundImage: 'url(/textures/earth_atmos_2048.jpg)',
    })
  })

  it('renders static fallback when WebGL is unavailable', () => {
    render(<EarthBackground forceDisableWebGL={true} />)
    const fallback = screen.getByTestId('earth-static-fallback')
    expect(fallback).toBeInTheDocument()
  })
})
