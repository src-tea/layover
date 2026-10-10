import { ArrowRight, CheckCircle2, Clock3, MapPinned, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import LayoverForm from '../components/LayoverForm';
import { formatConvertedUsd } from '../utils/currency';

const steps = [
  { title: 'Tell us your window', description: 'Share your airport, travel times, and baggage so the plan feels right from the start.' },
  { title: 'Find a travel buddy', description: 'Meet someone heading your way and compare storage options that match the provider rules.' },
  { title: 'Make the most of the hours', description: 'Explore a simple plan for food, wandering, and getting back to the terminal with ease.' },
];

const benefits = [
  'Thoughtful layover matching with real context in mind',
  'Clear storage rules and cost-sharing in plain language',
  'Warm, simple itinerary planning for a relaxed airport break',
  'Helpful safety reminders for solo travel and first-time users',
];

export default function LandingPage({ search, setSearch, onSubmit, errors, isLoading }) {
  return (
    <main className="page-shell">
      <section className="hero-section">
        <div className="container hero-grid">
          <div className="hero-copy">
            <div className="eyebrow">Travelling light starts here</div>
            <h1>A little time. A new way to travel.</h1>
            <p>
              Make the most of the hours between flights. Find a travel buddy, discover luggage storage that suits your plans, and keep your layover feeling easy.
            </p>
            <div className="cta-row">
              <Link className="btn btn-primary" to="/buddy">Plan my layover <ArrowRight size={16} /></Link>
              <a className="btn btn-secondary" href="#how-it-works">How it works</a>
            </div>
            <div className="microcopy">Meet someone heading your way, if you like. Your bag stays with an eligible provider — never by default with a stranger.</div>
          </div>

          <div className="hero-visual" aria-label="Warm travel photography for airport layover planning">
            <div className="hero-overlay-card">
              <span className="overlay-label">Illustrative estimate</span>
              <strong>{formatConvertedUsd(300, 'INR')}</strong>
              <small>Legacy INR example converted using ECB rates</small>
            </div>
          </div>
        </div>
      </section>

      <section className="container section-block hero-form-wrap">
        <div className="card-panel hero-form-card">
          <div className="hero-card-header">
            <div>
              <span className="eyebrow subtle">Plan your layover</span>
              <h2>Find the right window</h2>
            </div>
          </div>
          <LayoverForm values={search} onChange={setSearch} onSubmit={onSubmit} errors={errors} isLoading={isLoading} />
        </div>
      </section>

      <section id="how-it-works" className="container section-block">
        <div className="section-heading center-heading">
          <span className="eyebrow">How it works</span>
          <h2>Three gentle steps to a smoother layover</h2>
        </div>
        <div className="step-grid">
          {steps.map((step, index) => (
            <div className="card-panel step-card" key={step.title}>
              <div className="step-number">0{index + 1}</div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container section-block split-section">
        <div className="card-panel feature-panel">
          <span className="eyebrow">Why travellers use it</span>
          <h2>Simple, safe, and a little more human.</h2>
          <ul className="feature-list">
            {benefits.map((benefit) => (
              <li key={benefit}><CheckCircle2 size={16} /> {benefit}</li>
            ))}
          </ul>
        </div>

        <div className="card-panel feature-panel">
          <span className="eyebrow">Trusted by design</span>
          <h2>Clear rules, gentle reminders.</h2>
          <div className="safety-stack">
            <div className="mini-stat-row"><ShieldCheck size={16} /> Provider-managed storage only</div>
            <div className="mini-stat-row"><MapPinned size={16} /> Shared bookings shown only when permitted</div>
            <div className="mini-stat-row"><Clock3 size={16} /> Time windows checked before recommendations</div>
          </div>
        </div>
      </section>

      <section className="container section-block">
        <div className="calculator-panel card-panel">
          <div className="section-heading inline-heading">
            <span className="eyebrow">A little time, a little savings</span>
            <h2>See what you could save</h2>
          </div>
          <div className="calculator-display">
            <div>
              <span>Sample storage</span>
              <strong>{formatConvertedUsd(600, 'INR')}</strong>
            </div>
            <div>
              <span>Two travellers</span>
              <strong>{formatConvertedUsd(300, 'INR')} each</strong>
            </div>
            <div>
              <span>Potential saving</span>
              <strong>{formatConvertedUsd(300, 'INR')}</strong>
            </div>
          </div>
          <p className="price-provenance">Illustrative legacy examples, converted from INR at the ECB reference rate dated 2026-10-09. No provider price is verified.</p>
        </div>
      </section>
    </main>
  );
}
