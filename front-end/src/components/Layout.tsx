import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'

export function Navbar() {
  return (
    <header className="navbar">
      <NavLink className="brand" to="/">
        <span className="brand-mark">A</span>
        <span>
          ARIOS
          <small>Research Intelligence</small>
        </span>
      </NavLink>

      <nav aria-label="Main navigation">
        <NavLink to="/" end>Documents</NavLink>
        <NavLink to="/ingest">Ingest URL</NavLink>
        <NavLink to="/upload">Upload</NavLink>
        <NavLink to="/ask">Ask</NavLink>
      </nav>
    </header>
  )
}

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <>
      <Navbar />
      <main className="container">{children}</main>
      <footer>ARIOS · AI Research Intelligence OS</footer>
    </>
  )
}
