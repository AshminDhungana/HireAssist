import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

vi.mock('../hooks/useApiStatus', () => ({
  useApiStatus: vi.fn(() => ({
    isOnline: true,
    message: 'Connected',
    color: 'green',
  })),
}))

describe('App Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('renders HireAssist title', () => {
    render(<App />)
    expect(screen.getByText('HireAssist')).toBeInTheDocument()
  })

  it('renders login form by default', () => {
    render(<App />)
    expect(screen.getByText(/Welcome Back/i)).toBeInTheDocument()
    // Get first Login button (navigation button)
    const loginButtons = screen.getAllByRole('button', { name: /Login/i })
    expect(loginButtons.length).toBeGreaterThan(0)
    expect(screen.getByPlaceholderText('you@example.com')).toBeInTheDocument()
  })

  it('renders guest upload button', () => {
    render(<App />)
    expect(screen.getByRole('button', { name: /Guest Upload/i })).toBeInTheDocument()
  })

  it('renders api status indicator', () => {
    render(<App />)
    expect(screen.getByText(/Connected/i)).toBeInTheDocument()
  })

  it('renders sign up option', () => {
    render(<App />)
    expect(screen.getByText(/Don't have an account/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Sign Up/i })).toBeInTheDocument()
  })
})
