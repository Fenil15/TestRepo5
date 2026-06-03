import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Customers from './Customers'

type Customer = {
  id: string
  name: string
  email: string
  phone: string | null
  company: string | null
  address: string | null
}

function makeCustomer(overrides: Partial<Customer> = {}): Customer {
  return {
    id: 'c1',
    name: 'Alice',
    email: 'alice@example.com',
    phone: '555-1234',
    company: 'Acme',
    address: '123 Main St',
    ...overrides,
  }
}

/** Build a Response-like object good enough for the component's use of fetch. */
function jsonResponse(body: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: () => Promise.resolve(body),
  } as unknown as Response
}

/** Wrap a Customer array in the paginated envelope the component expects. */
function pageResponse(items: Customer[]): Response {
  return jsonResponse({ items, total: items.length, page: 1, page_size: 10 })
}

const fetchMock = vi.fn()

beforeEach(() => {
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  fetchMock.mockReset()
})

describe('Customers page', () => {
  it('shows a loading indicator before customers resolve', () => {
    // Never resolve so the loading state stays visible.
    fetchMock.mockReturnValue(new Promise(() => {}))
    render(<Customers />)
    expect(screen.getByText('Loading customers…')).toBeInTheDocument()
  })

  it('renders an error message when the initial fetch fails', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(null, false, 500))
    render(<Customers />)
    expect(
      await screen.findByText('Failed to load customers. Please refresh.'),
    ).toBeInTheDocument()
  })

  it('renders an error message when fetch rejects', async () => {
    fetchMock.mockRejectedValueOnce(new Error('network down'))
    render(<Customers />)
    expect(
      await screen.findByText('Failed to load customers. Please refresh.'),
    ).toBeInTheDocument()
  })

  it('renders an empty-state row when there are no customers', async () => {
    fetchMock.mockResolvedValueOnce(pageResponse([]))
    render(<Customers />)
    expect(
      await screen.findByText('No customers yet. Add one below.'),
    ).toBeInTheDocument()
  })

  it('renders customer rows once loaded', async () => {
    fetchMock.mockResolvedValueOnce(
      pageResponse([makeCustomer(), makeCustomer({ id: 'c2', name: 'Bob', email: 'bob@example.com' })]),
    )
    render(<Customers />)

    expect(await screen.findByText('Alice')).toBeInTheDocument()
    expect(screen.getByText('alice@example.com')).toBeInTheDocument()
    expect(screen.getByText('Bob')).toBeInTheDocument()
    expect(screen.getByText('bob@example.com')).toBeInTheDocument()
  })

  it('renders blank cells for null optional fields', async () => {
    fetchMock.mockResolvedValueOnce(
      pageResponse([makeCustomer({ phone: null, company: null, address: null })]),
    )
    render(<Customers />)

    const nameCell = await screen.findByText('Alice')
    const row = nameCell.closest('tr')!
    const cells = within(row).getAllByRole('cell')
    // Cells: name, email, phone, company, address, actions
    expect(cells[2]).toBeEmptyDOMElement()
    expect(cells[3]).toBeEmptyDOMElement()
    expect(cells[4]).toBeEmptyDOMElement()
  })

  it('submits a new customer and refreshes the list', async () => {
    const user = userEvent.setup()
    const carol = makeCustomer({ id: 'new', name: 'Carol', email: 'carol@example.com' })
    fetchMock
      // initial load
      .mockResolvedValueOnce(pageResponse([]))
      // POST create
      .mockResolvedValueOnce(jsonResponse(carol, true, 201))
      // refresh load
      .mockResolvedValueOnce(pageResponse([carol]))

    render(<Customers />)
    await screen.findByText('No customers yet. Add one below.')

    await user.type(screen.getByLabelText('Name *'), 'Carol')
    await user.type(screen.getByLabelText('Email *'), 'carol@example.com')
    await user.type(screen.getByLabelText('Phone'), '555-9999')
    await user.click(screen.getByRole('button', { name: 'Add Customer' }))

    expect(await screen.findByText('Carol')).toBeInTheDocument()

    // Verify the POST body only includes filled-in fields.
    const postCall = fetchMock.mock.calls.find(([url, opts]) => url === '/api/customers' && opts?.method === 'POST')
    expect(postCall).toBeTruthy()
    const body = JSON.parse((postCall![1] as RequestInit).body as string)
    expect(body).toEqual({ name: 'Carol', email: 'carol@example.com', phone: '555-9999' })

    // Add form should be reset after success.
    expect(screen.getByLabelText('Name *')).toHaveValue('')
    expect(screen.getByLabelText('Email *')).toHaveValue('')
  })

  it('shows an error when adding a customer fails', async () => {
    const user = userEvent.setup()
    fetchMock
      .mockResolvedValueOnce(pageResponse([]))
      .mockResolvedValueOnce(jsonResponse(null, false, 500))

    render(<Customers />)
    await screen.findByText('No customers yet. Add one below.')

    await user.type(screen.getByLabelText('Name *'), 'Carol')
    await user.type(screen.getByLabelText('Email *'), 'carol@example.com')
    await user.click(screen.getByRole('button', { name: 'Add Customer' }))

    expect(
      await screen.findByText('Failed to add customer. Please try again.'),
    ).toBeInTheDocument()
  })

  it('edits a customer and saves the changes', async () => {
    const user = userEvent.setup()
    fetchMock
      .mockResolvedValueOnce(pageResponse([makeCustomer()]))
      // PUT update
      .mockResolvedValueOnce(jsonResponse(makeCustomer({ name: 'Alice Updated' })))
      // refresh load
      .mockResolvedValueOnce(pageResponse([makeCustomer({ name: 'Alice Updated' })]))

    render(<Customers />)
    await screen.findByText('Alice')

    await user.click(screen.getByRole('button', { name: 'Edit' }))

    const nameInput = screen.getByDisplayValue('Alice')
    await user.clear(nameInput)
    await user.type(nameInput, 'Alice Updated')
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(await screen.findByText('Alice Updated')).toBeInTheDocument()

    const putCall = fetchMock.mock.calls.find(([url, opts]) => url === '/api/customers/c1' && opts?.method === 'PUT')
    expect(putCall).toBeTruthy()
    const body = JSON.parse((putCall![1] as RequestInit).body as string)
    expect(body.name).toBe('Alice Updated')
  })

  it('cancels an edit without calling the API', async () => {
    const user = userEvent.setup()
    fetchMock.mockResolvedValueOnce(pageResponse([makeCustomer()]))

    render(<Customers />)
    await screen.findByText('Alice')

    await user.click(screen.getByRole('button', { name: 'Edit' }))
    expect(screen.getByDisplayValue('Alice')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    // Back to read-only row, no PUT made (only the initial GET).
    expect(screen.getByText('Alice')).toBeInTheDocument()
    expect(screen.queryByDisplayValue('Alice')).not.toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('shows an error when saving an edit fails', async () => {
    const user = userEvent.setup()
    fetchMock
      .mockResolvedValueOnce(pageResponse([makeCustomer()]))
      .mockResolvedValueOnce(jsonResponse(null, false, 500))

    render(<Customers />)
    await screen.findByText('Alice')

    await user.click(screen.getByRole('button', { name: 'Edit' }))
    await user.click(screen.getByRole('button', { name: 'Save' }))

    expect(
      await screen.findByText('Failed to save changes. Please try again.'),
    ).toBeInTheDocument()
  })

  it('deletes a customer and refreshes the list', async () => {
    const user = userEvent.setup()
    fetchMock
      .mockResolvedValueOnce(pageResponse([makeCustomer()]))
      // DELETE
      .mockResolvedValueOnce(jsonResponse(null, true, 204))
      // refresh load -> now empty
      .mockResolvedValueOnce(pageResponse([]))

    render(<Customers />)
    await screen.findByText('Alice')

    await user.click(screen.getByRole('button', { name: 'Delete' }))

    expect(
      await screen.findByText('No customers yet. Add one below.'),
    ).toBeInTheDocument()

    const deleteCall = fetchMock.mock.calls.find(([url, opts]) => url === '/api/customers/c1' && opts?.method === 'DELETE')
    expect(deleteCall).toBeTruthy()
  })

  it('still refreshes the list when a delete request fails', async () => {
    const user = userEvent.setup()
    fetchMock
      .mockResolvedValueOnce(pageResponse([makeCustomer()]))
      // DELETE fails
      .mockRejectedValueOnce(new Error('boom'))
      // refresh load still happens
      .mockResolvedValueOnce(pageResponse([makeCustomer()]))

    render(<Customers />)
    await screen.findByText('Alice')

    await user.click(screen.getByRole('button', { name: 'Delete' }))

    await waitFor(() => {
      const refreshCalls = fetchMock.mock.calls.filter(
        ([url, opts]) => (url as string).startsWith('/api/customers') && (opts === undefined || opts.method === undefined),
      )
      expect(refreshCalls.length).toBe(2)
    })
  })
})
