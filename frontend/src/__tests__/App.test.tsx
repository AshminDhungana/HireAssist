import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App Component', () => {
  it('renders HireAssist title', () => {
    render(<App />)
    expect(screen.getByText('HireAssist')).toBeInTheDocument()
  })

  it('renders navigation buttons', () => {
    render(<App />)
    expect(screen.getByText(/Resume Upload/)).toBeInTheDocument()
    expect(screen.getByText(/Parser Comparison/)).toBeInTheDocument()
  })
})
