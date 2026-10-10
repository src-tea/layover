import { CheckCircle2, ShieldAlert, UserRound, WalletCards } from 'lucide-react';

const checklist = [
  'Only approved storage providers should be used.',
  'Check prohibited-item rules before storing bags.',
  'Never accept luggage from strangers.',
  'Keep booking details and personal information secure.',
  'Confirm visa, immigration, and airline requirements before leaving the airport.',
];

export default function ProfilePage() {
  return (
    <main className="page-shell">
      <div className="container profile-layout">
        <div className="card-panel profile-card">
          <div className="profile-header">
            <div className="avatar-wrap large">SD</div>
            <div>
              <h2>Sana Dutta</h2>
              <p>Verified traveller profile</p>
            </div>
          </div>

          <div className="meta-grid compact-grid">
            <div><UserRound size={14} /> Travel interests: food, shopping</div>
            <div><WalletCards size={14} /> Baggage: Carry-on + 1 checked bag</div>
          </div>

          <div className="card-panel muted-panel">
            <h3>Contact sharing</h3>
            <ul className="feature-list">
              <li>Email: shared with approved connections</li>
              <li>Phone: only shown after a confirmed connection request</li>
            </ul>
          </div>

          <div className="card-panel muted-panel">
            <h3>Safety checklist</h3>
            <ul className="feature-list">
              {checklist.map((item) => (
                <li key={item}><CheckCircle2 size={16} /> {item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="sidebar-stack">
          <div className="card-panel">
            <h3>Report or help</h3>
            <button className="btn btn-secondary full" type="button">Report issue</button>
            <div className="alert-box warning-box">
              <ShieldAlert size={16} /> We review support requests from verified travellers within 24 hours.
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
