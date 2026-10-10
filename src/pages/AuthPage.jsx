import { useState } from 'react';
import { apiFetch } from '../lib/api';

const initialForm = {
  fullName: '',
  email: '',
  phone: '',
  password: '',
  identifier: '',
};

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState({ type: '', message: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setStatus({ type: '', message: '' });
    setIsSubmitting(true);

    try {
      if (mode === 'login') {
        if (!form.identifier.trim() || !form.password) {
          throw new Error('Both login identifier and password are required.');
        }

        const payload = {
          identifier: form.identifier,
          password: form.password,
        };

        const result = await apiFetch('/auth/login', {
          method: 'POST',
          body: JSON.stringify(payload),
        });

        localStorage.setItem('layover-auth-token', result.token || '');
        localStorage.setItem('layover-auth-user', JSON.stringify(result.user || {}));
        onAuthenticated?.(result.user || {});
        setStatus({ type: 'success', message: 'Signed in successfully.' });
        return;
      }

      const fullName = form.fullName.trim();
      const email = form.email.trim();
      const phone = form.phone.trim();

      if (fullName.length < 2) {
        throw new Error('Enter your full name (at least 2 characters).');
      }
      if (!form.password || form.password.length < 8) {
        throw new Error('Your password must be at least 8 characters.');
      }
      if (!email && !phone) {
        throw new Error('Please provide a full name, a password, and either an email or phone number.');
      }

      const payload = {
        full_name: fullName,
        email: email || undefined,
        phone: phone || undefined,
        password: form.password,
      };

      await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setStatus({ type: 'success', message: 'Account created. You can now log in.' });
      setMode('login');
      setForm({ ...initialForm, identifier: form.email || form.phone || '' });
    } catch (error) {
      setStatus({ type: 'error', message: error.message || 'Authentication failed.' });
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  return (
    <main className="page-shell">
      <div className="container auth-layout">
        <section className="auth-intro" aria-label="LAYOVER account">
          <span className="auth-kicker">A better kind of layover</span>
          <h1>{mode === 'login' ? 'Travel, with a little more ease.' : 'Make room for good company.'}</h1>
          <p>Meet fellow travellers, plan the hours between flights, and keep your details in your hands.</p>
          <div className="auth-note">
            <span className="auth-note-mark" aria-hidden="true">01</span>
            <span>Contact details stay private until you choose to share them.</span>
          </div>
        </section>

        <section className="auth-card" aria-labelledby="auth-title">
          <div className="auth-header">
            <span className="auth-eyebrow">Your travel profile</span>
            <h2 id="auth-title">{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
            <p>{mode === 'login' ? 'Log in to pick up where your journey left off.' : 'One profile for smoother airport layovers.'}</p>
          </div>

          <div className="auth-toggle" aria-label="Authentication mode">
            <button
              type="button"
              className={mode === 'login' ? 'auth-tab active' : 'auth-tab'}
              aria-pressed={mode === 'login'}
              onClick={() => { setMode('login'); setStatus({ type: '', message: '' }); }}
            >
              Log in
            </button>
            <button
              type="button"
              className={mode === 'register' ? 'auth-tab active' : 'auth-tab'}
              aria-pressed={mode === 'register'}
              onClick={() => { setMode('register'); setStatus({ type: '', message: '' }); }}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="stack-form">
            {mode === 'register' && (
              <>
                <label className="auth-field">
                  Full name
                  <input autoComplete="name" minLength={2} maxLength={120} required value={form.fullName} onChange={(event) => updateField('fullName', event.target.value)} />
                </label>
                <label className="auth-field">
                  Email
                  <input autoComplete="email" type="email" value={form.email} onChange={(event) => updateField('email', event.target.value)} placeholder="you@example.com" />
                </label>
                <label className="auth-field">
                  Phone
                  <input autoComplete="tel" type="tel" value={form.phone} onChange={(event) => updateField('phone', event.target.value)} placeholder="+1 555 123 4567" />
                </label>
              </>
            )}

            {mode === 'login' && (
              <label className="auth-field">
                Email or phone
                <input autoComplete="username" required value={form.identifier} onChange={(event) => updateField('identifier', event.target.value)} placeholder="name@example.com or +1 555 123 4567" />
              </label>
            )}

            <label className="auth-field">
              Password
              <input autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={8} required type="password" value={form.password} onChange={(event) => updateField('password', event.target.value)} />
            </label>

            {status.message ? (
              <div role="status" aria-live="polite" className={`auth-message ${status.type}`}>
                {status.message}
              </div>
            ) : null}

            <button type="submit" className="auth-submit" disabled={isSubmitting}>
              {isSubmitting ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
            </button>
          </form>
          {mode === 'register' ? <p className="auth-footnote">By creating an account, you agree to keep your contact details private and share them only when you choose.</p> : null}
        </section>
      </div>
    </main>
  );
}
