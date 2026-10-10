import { Link, NavLink } from 'react-router-dom';
import { PlaneTakeoff, Menu, ShieldCheck } from 'lucide-react';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Find a Buddy', to: '/buddy' },
  { label: 'Luggage Storage', to: '/storage' },
  { label: 'My Layover', to: '/layover' },
];

export default function Navbar() {
  return (
    <header className="topbar">
      <div className="container nav-shell">
        <Link to="/" className="brand" aria-label="LAYOVER home">
          <span className="brand-mark"><PlaneTakeoff size={18} /></span>
          <span>LAYOVER</span>
        </Link>

        <nav className="desktop-nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="nav-actions">
          <Link className="btn btn-secondary small" to="/login">Log in</Link>
          <Link className="btn btn-primary small" to="/buddy">Plan my layover</Link>
          <button className="mobile-menu" type="button" aria-label="Open navigation menu">
            <Menu size={18} />
          </button>
        </div>
      </div>
    </header>
  );
}
