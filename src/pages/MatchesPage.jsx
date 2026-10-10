import { Filter, Sparkles } from 'lucide-react';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import { findMatches, sortMatches } from '../utils/matching';
import { travellers } from '../data/travellers';

export default function MatchesPage({
  search,
  candidates = travellers,
  connectionRequests = { incoming: [], outgoing: [], active: [] },
  connectionMessage,
  onViewMatch,
  onConnect,
  onRespondToRequest,
  onDisconnect,
  onReset,
}) {
  const activeUserIds = new Set((connectionRequests.active || []).map(({ user }) => user?.id).filter(Boolean));
  const eligibleCandidates = candidates.filter((candidate) => !activeUserIds.has(candidate.userId));
  const allMatches = sortMatches(findMatches(search, eligibleCandidates), search);

  return (
    <main className="page-shell">
      <div className="container">
        {connectionMessage ? <div className="alert-box info-box connection-message" role="status">{connectionMessage}</div> : null}

        {connectionRequests.active?.length ? (
          <section className="connection-section" aria-labelledby="active-pair-title">
            <h2 id="active-pair-title">Your connection</h2>
            <div className="connection-list">
              {connectionRequests.active.map(({ connection, user }) => (
                <article className="connection-row" key={connection.id}>
                  <div>
                    <h3>{user?.display_name || user?.full_name || 'Connected traveller'}</h3>
                    <p>
                      {[user?.email, user?.phone].filter(Boolean).join(' · ') || 'No contact details shared'}
                    </p>
                  </div>
                  <button className="btn btn-secondary small" type="button" onClick={() => onDisconnect(connection)}>
                    Disconnect
                  </button>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {connectionRequests.incoming?.length ? (
          <section className="connection-section" aria-labelledby="incoming-requests-title">
            <h2 id="incoming-requests-title">Connection requests</h2>
            <div className="connection-list">
              {connectionRequests.incoming.filter((request) => request.status === 'pending').map((request) => (
                <article className="connection-row" key={request.id}>
                  <div>
                    <h3>{request.other_user?.display_name || request.other_user?.full_name || 'A traveller'}</h3>
                    <p>Would like to connect with you</p>
                  </div>
                  <div className="action-row connection-controls">
                    <button className="btn btn-primary small" type="button" onClick={() => onRespondToRequest(request, 'accepted')}>Accept</button>
                    <button className="btn btn-secondary small" type="button" onClick={() => onRespondToRequest(request, 'declined')}>Decline</button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        {connectionRequests.outgoing?.some((request) => request.status === 'pending') ? (
          <section className="connection-section" aria-labelledby="sent-requests-title">
            <h2 id="sent-requests-title">Sent requests</h2>
            <div className="connection-list">
              {connectionRequests.outgoing.filter((request) => request.status === 'pending').map((request) => (
                <article className="connection-row" key={request.id}>
                  <div>
                    <h3>{request.other_user?.display_name || request.other_user?.full_name || 'A traveller'}</h3>
                    <p>Waiting for a response</p>
                  </div>
                  <button className="btn btn-secondary small" type="button" onClick={() => onRespondToRequest(request, 'cancelled')}>Cancel request</button>
                </article>
              ))}
            </div>
          </section>
        ) : null}

        <div className="section-heading inline-heading">
          <div>
            <span className="eyebrow">Find a match</span>
            <h2>People who fit your layover</h2>
          </div>
          {allMatches.length ? <div className="filter-pill"><Filter size={14} /> Sorted by best schedule match</div> : null}
        </div>

        {allMatches.length ? (
          <>
            <div className="toolbar-row">
              <span className="muted"><Sparkles size={14} /> Compatibility estimates based on your layover</span>
            </div>
            <div className="results-grid">
              {allMatches.map((traveller) => {
                const requestPending = connectionRequests.outgoing?.some(
                  (request) => request.status === 'pending' && request.user_b_id === traveller.userId,
                );
                return (
                  <MatchCard
                    key={traveller.id}
                    traveller={traveller}
                    connectionStatus={requestPending ? 'Request pending' : null}
                    onView={() => onViewMatch(traveller)}
                    onConnect={() => onConnect(traveller)}
                  />
                );
              })}
            </div>
          </>
        ) : (
          <div className="narrow-shell">
            <EmptyState
              title="No compatible travellers found"
              message="Your layover rules are strict, or the airport window is too tight for a shared booking. Try changing your search criteria or switch to a solo-storage path."
              action={{ label: 'Adjust search', onClick: onReset }}
            />
          </div>
        )}
      </div>
    </main>
  );
}
