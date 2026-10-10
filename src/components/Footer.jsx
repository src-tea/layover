import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="container footer-grid">
        <div>
          <div className="footer-brand">LAYOVER</div>
          <p>Demo-only travel planning for smarter airport layovers.</p>
        </div>
        <div>
          <h4>Company</h4>
          <ul>
            <li><Link to="/">About</Link></li>
            <li><Link to="/profile">Safety</Link></li>
            <li><Link to="/trips">Help</Link></li>
          </ul>
        </div>
        <div>
          <h4>Support</h4>
          <ul>
            <li><Link to="/profile">Privacy</Link></li>
            <li><Link to="/explore">Explore</Link></li>
            <li><Link to="/matches">Matches</Link></li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
