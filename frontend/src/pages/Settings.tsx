import { useEffect, useMemo, useState } from 'react'
import './Settings.css'

type Theme = 'system' | 'light' | 'dark'
type Density = 'comfortable' | 'compact'

type Settings = {
  displayName: string
  theme: Theme
  density: Density
  itemsPerPage: number
  emailNotifications: boolean
}

const STORAGE_KEY = 'app-settings'

const ITEMS_PER_PAGE_OPTIONS = [10, 25, 50, 100] as const

const defaultSettings: Settings = {
  displayName: '',
  theme: 'system',
  density: 'comfortable',
  itemsPerPage: 10,
  emailNotifications: true,
}

function isTheme(value: unknown): value is Theme {
  return value === 'system' || value === 'light' || value === 'dark'
}

function isDensity(value: unknown): value is Density {
  return value === 'comfortable' || value === 'compact'
}

/**
 * Read persisted settings from localStorage, tolerating missing/corrupt data
 * and unknown fields by falling back to defaults on a per-field basis.
 */
function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultSettings
    const parsed = JSON.parse(raw) as Partial<Record<keyof Settings, unknown>>
    return {
      displayName:
        typeof parsed.displayName === 'string'
          ? parsed.displayName
          : defaultSettings.displayName,
      theme: isTheme(parsed.theme) ? parsed.theme : defaultSettings.theme,
      density: isDensity(parsed.density)
        ? parsed.density
        : defaultSettings.density,
      itemsPerPage: ITEMS_PER_PAGE_OPTIONS.includes(
        parsed.itemsPerPage as (typeof ITEMS_PER_PAGE_OPTIONS)[number],
      )
        ? (parsed.itemsPerPage as number)
        : defaultSettings.itemsPerPage,
      emailNotifications:
        typeof parsed.emailNotifications === 'boolean'
          ? parsed.emailNotifications
          : defaultSettings.emailNotifications,
    }
  } catch {
    return defaultSettings
  }
}

function Settings() {
  const [saved, setSaved] = useState<Settings>(() => loadSettings())
  const [form, setForm] = useState<Settings>(saved)
  const [justSaved, setJustSaved] = useState(false)

  // Clear the "Saved" confirmation shortly after it appears.
  useEffect(() => {
    if (!justSaved) return
    const handle = setTimeout(() => setJustSaved(false), 2000)
    return () => clearTimeout(handle)
  }, [justSaved])

  const isDirty = useMemo(
    () => JSON.stringify(form) !== JSON.stringify(saved),
    [form, saved],
  )

  function update<K extends keyof Settings>(key: K, value: Settings[K]) {
    setForm((prev) => ({ ...prev, [key]: value }))
    setJustSaved(false)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    localStorage.setItem(STORAGE_KEY, JSON.stringify(form))
    setSaved(form)
    setJustSaved(true)
  }

  function handleReset() {
    setForm(defaultSettings)
    setJustSaved(false)
  }

  return (
    <main className="settings-page">
      <h1>Settings</h1>
      <p className="settings-subtitle">
        Manage your account preferences. Changes are saved to this browser.
      </p>

      <form className="settings-form" onSubmit={handleSubmit}>
        <section className="settings-section">
          <h2>Profile</h2>
          <div className="settings-field">
            <label htmlFor="settings-display-name">Display name</label>
            <input
              id="settings-display-name"
              className="settings-input"
              type="text"
              value={form.displayName}
              placeholder="Your name"
              onChange={(e) => update('displayName', e.target.value)}
            />
          </div>
        </section>

        <section className="settings-section">
          <h2>Appearance</h2>
          <div className="settings-field">
            <label htmlFor="settings-theme">Theme</label>
            <select
              id="settings-theme"
              className="settings-input"
              value={form.theme}
              onChange={(e) => update('theme', e.target.value as Theme)}
            >
              <option value="system">System</option>
              <option value="light">Light</option>
              <option value="dark">Dark</option>
            </select>
          </div>
          <div className="settings-field">
            <label htmlFor="settings-density">Table density</label>
            <select
              id="settings-density"
              className="settings-input"
              value={form.density}
              onChange={(e) => update('density', e.target.value as Density)}
            >
              <option value="comfortable">Comfortable</option>
              <option value="compact">Compact</option>
            </select>
          </div>
        </section>

        <section className="settings-section">
          <h2>Preferences</h2>
          <div className="settings-field">
            <label htmlFor="settings-items-per-page">Items per page</label>
            <select
              id="settings-items-per-page"
              className="settings-input"
              value={form.itemsPerPage}
              onChange={(e) =>
                update('itemsPerPage', Number(e.target.value))
              }
            >
              {ITEMS_PER_PAGE_OPTIONS.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </div>
          <div className="settings-field settings-field--checkbox">
            <input
              id="settings-email-notifications"
              type="checkbox"
              checked={form.emailNotifications}
              onChange={(e) =>
                update('emailNotifications', e.target.checked)
              }
            />
            <label htmlFor="settings-email-notifications">
              Email notifications
            </label>
          </div>
        </section>

        <div className="settings-actions">
          <button
            type="submit"
            className="settings-btn settings-btn--save"
            disabled={!isDirty}
          >
            Save changes
          </button>
          <button
            type="button"
            className="settings-btn settings-btn--reset"
            onClick={handleReset}
          >
            Reset to defaults
          </button>
          {justSaved && (
            <span className="settings-saved" role="status">
              Saved
            </span>
          )}
        </div>
      </form>
    </main>
  )
}

export default Settings
