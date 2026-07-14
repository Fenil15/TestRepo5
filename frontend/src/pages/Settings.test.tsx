import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Settings from './Settings'

const STORAGE_KEY = 'app-settings'

describe('Settings', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('renders the settings sections with default values', () => {
    render(<Settings />)

    expect(
      screen.getByRole('heading', { name: 'Settings' }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Display name')).toHaveValue('')
    expect(screen.getByLabelText('Theme')).toHaveValue('system')
    expect(screen.getByLabelText('Table density')).toHaveValue('comfortable')
    expect(screen.getByLabelText('Items per page')).toHaveValue('10')
    expect(screen.getByLabelText('Email notifications')).toBeChecked()
  })

  it('disables Save until a change is made', async () => {
    const user = userEvent.setup()
    render(<Settings />)

    const save = screen.getByRole('button', { name: 'Save changes' })
    expect(save).toBeDisabled()

    await user.type(screen.getByLabelText('Display name'), 'Ada')
    expect(save).toBeEnabled()
  })

  it('persists settings to localStorage on save', async () => {
    const user = userEvent.setup()
    render(<Settings />)

    await user.type(screen.getByLabelText('Display name'), 'Ada Lovelace')
    await user.selectOptions(screen.getByLabelText('Theme'), 'dark')
    await user.selectOptions(screen.getByLabelText('Items per page'), '50')
    await user.click(screen.getByLabelText('Email notifications'))
    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    expect(screen.getByRole('status')).toHaveTextContent('Saved')

    const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}')
    expect(stored).toMatchObject({
      displayName: 'Ada Lovelace',
      theme: 'dark',
      itemsPerPage: 50,
      emailNotifications: false,
    })

    // Save should be disabled again since form now matches saved state.
    expect(screen.getByRole('button', { name: 'Save changes' })).toBeDisabled()
  })

  it('loads previously saved settings from localStorage', () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        displayName: 'Grace',
        theme: 'light',
        density: 'compact',
        itemsPerPage: 25,
        emailNotifications: false,
      }),
    )

    render(<Settings />)

    expect(screen.getByLabelText('Display name')).toHaveValue('Grace')
    expect(screen.getByLabelText('Theme')).toHaveValue('light')
    expect(screen.getByLabelText('Table density')).toHaveValue('compact')
    expect(screen.getByLabelText('Items per page')).toHaveValue('25')
    expect(screen.getByLabelText('Email notifications')).not.toBeChecked()
  })

  it('falls back to defaults when stored data is corrupt', () => {
    localStorage.setItem(STORAGE_KEY, 'not-json{')

    render(<Settings />)

    expect(screen.getByLabelText('Theme')).toHaveValue('system')
    expect(screen.getByLabelText('Items per page')).toHaveValue('10')
  })

  it('resets the form to defaults', async () => {
    const user = userEvent.setup()
    render(<Settings />)

    await user.type(screen.getByLabelText('Display name'), 'Temp')
    await user.selectOptions(screen.getByLabelText('Theme'), 'dark')
    await user.click(screen.getByRole('button', { name: 'Reset to defaults' }))

    expect(screen.getByLabelText('Display name')).toHaveValue('')
    expect(screen.getByLabelText('Theme')).toHaveValue('system')
  })

  it('reset only stages defaults until Save is clicked', async () => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        displayName: 'Grace',
        theme: 'light',
        density: 'compact',
        itemsPerPage: 25,
        emailNotifications: false,
      }),
    )
    const user = userEvent.setup()
    render(<Settings />)

    await user.click(screen.getByRole('button', { name: 'Reset to defaults' }))

    // Form shows defaults, but persisted storage is untouched until Save.
    expect(screen.getByLabelText('Display name')).toHaveValue('')
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}')).toMatchObject({
      displayName: 'Grace',
    })

    // Since defaults differ from saved state, Save is enabled; clicking it persists.
    const save = screen.getByRole('button', { name: 'Save changes' })
    expect(save).toBeEnabled()
    await user.click(save)
    expect(JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '{}')).toMatchObject({
      displayName: '',
      theme: 'system',
    })
  })

  it('shows an error and does not confirm when saving fails', async () => {
    const user = userEvent.setup()
    const setItem = vi
      .spyOn(Storage.prototype, 'setItem')
      .mockImplementation(() => {
        throw new Error('QuotaExceededError')
      })

    render(<Settings />)
    await user.type(screen.getByLabelText('Display name'), 'Ada')
    await user.click(screen.getByRole('button', { name: 'Save changes' }))

    expect(screen.getByRole('alert')).toHaveTextContent(/could not save/i)
    expect(screen.queryByRole('status')).not.toBeInTheDocument()

    setItem.mockRestore()
  })
})
