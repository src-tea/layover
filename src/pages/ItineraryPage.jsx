import { Clock3, Plane, TimerReset } from 'lucide-react';
import { useMemo } from 'react';
import ItineraryTimeline from '../components/ItineraryTimeline';
import { calculateUsableLayover } from '../utils/itinerary';
import { attractions } from '../data/attractions';

export default function ItineraryPage({ search, activities = [], returnBuffer = 30 }) {
  const selectedActivities = useMemo(() => attractions.filter((place) => activities.includes(place.id)), [activities]);
  const totalMinutes = search.arrival && search.departure
    ? Math.max(0, (new Date(search.departure) - new Date(search.arrival)) / 60000)
    : 0;
  const usable = calculateUsableLayover(totalMinutes, 20, 25, returnBuffer);
  const plannedMinutes = selectedActivities.reduce((sum, item) => sum + Number(item.durationMinutes || 60), 0);
  const warning = plannedMinutes > usable;

  return (
    <main className="page-shell">
      <div className="container itinerary-layout">
        <div className="card-panel">
          <div className="section-heading inline-heading">
            <div>
              <span className="eyebrow">Smart layover itinerary</span>
              <h2>City plan and airport return</h2>
            </div>
          </div>

          <div className="summary-card compact big-gap">
            <div><span>Layover</span><strong>{Math.round(totalMinutes)} min</strong></div>
            <div><span>Usable time</span><strong>{Math.round(usable)} min</strong></div>
            <div><span>Return buffer</span><strong>{returnBuffer} min</strong></div>
          </div>

          <div className="countdown-box">
            <Plane size={18} />
            <div>
              <span>Sample departure</span>
              <strong>{search.departure ? new Date(search.departure).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '—'}</strong>
            </div>
          </div>

          {warning ? <div className="alert-box warning-box">The itinerary is tight. Sample activities exceed the suggested safe buffer. Actual immigration, check-in, and boarding requirements should be checked before leaving the airport.</div> : null}

          <ItineraryTimeline items={selectedActivities.map((item) => ({ ...item, travelTime: item.travelTime, duration: item.duration }))} />
        </div>

        <aside className="sidebar-stack">
          <div className="card-panel">
            <h3>Trip notes</h3>
            <ul className="summary-list">
              <li><span>Storage drop-off</span><strong>Approx. 15 min</strong></li>
              <li><span>Selected activities</span><strong>{selectedActivities.length}</strong></li>
              <li><span>Planned travel</span><strong>{selectedActivities.length * 12} min</strong></li>
              <li><span>Airport return</span><strong>{returnBuffer} min buffer</strong></li>
            </ul>
          </div>
        </aside>
      </div>
    </main>
  );
}
