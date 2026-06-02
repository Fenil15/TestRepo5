import { useCallback, useEffect, useReducer, useState } from 'react'
import './Customers.css'

type Customer = {
  id: string
  name: string
  email: string
  phone: string | null
  company: string | null
  address: string | null
}

type CustomerPage = {
  items: Customer[]
  total: number
  page: number
  page_size: number
}

type SortField = 'name' | 'email' | 'company'
type SortDir = 'asc' | 'desc'

const PAGE_SIZE = 10

type FormData = {
  name: string
  email: string
  phone: string
  company: string
  address: string
}

type EditState = {
  id: string
  data: FormData
}

type CustomerListState =
  | { status: 'loading' }
  | { status: 'ok'; customers: Customer[]; total: number }
  | { status: 'error' }

type CustomerListAction =
  | { type: 'loaded'; customers: Customer[]; total: number }
  | { type: 'failed' }

function customerListReducer(
  _state: CustomerListState,
  action: CustomerListAction,
): CustomerListState {
  if (action.type === 'loaded')
    return { status: 'ok', customers: action.customers, total: action.total }
  return { status: 'error' }
}

const emptyForm: FormData = {
  name: '',
  email: '',
  phone: '',
  company: '',
  address: '',
}

function customerToFormData(c: Customer): FormData {
  return {
    name: c.name,
    email: c.email,
    phone: c.phone ?? '',
    company: c.company ?? '',
    address: c.address ?? '',
  }
}

type SortableHeaderProps = {
  label: string
  field: SortField
  activeField: SortField
  dir: SortDir
  onSort: (field: SortField) => void
}

function SortableHeader({ label, field, activeField, dir, onSort }: SortableHeaderProps) {
  const isActive = field === activeField
  const ascending = dir === 'asc'
  const indicator = isActive ? (ascending ? '▲' : '▼') : ''
  return (
    <th
      className={`customers-th-sortable${isActive ? ' customers-th-sortable--active' : ''}`}
      aria-sort={isActive ? (ascending ? 'ascending' : 'descending') : 'none'}
    >
      <button
        type="button"
        className="customers-sort-btn"
        onClick={() => onSort(field)}
      >
        {label}
        <span className="customers-sort-indicator">{indicator}</span>
      </button>
    </th>
  )
}

function Customers() {
  const [listState, dispatch] = useReducer(customerListReducer, { status: 'loading' })
  const [refreshToken, setRefreshToken] = useState<number>(0)
  const [addForm, setAddForm] = useState<FormData>(emptyForm)
  const [addError, setAddError] = useState<string>('')
  const [editState, setEditState] = useState<EditState | null>(null)
  const [editError, setEditError] = useState<string>('')

  // Search / sort / pagination state.
  const [searchInput, setSearchInput] = useState<string>('')
  const [search, setSearch] = useState<string>('')
  const [sortField, setSortField] = useState<SortField>('name')
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [page, setPage] = useState<number>(1)

  const triggerRefresh = useCallback(() => {
    setRefreshToken((t) => t + 1)
  }, [])

  // Debounce the search box so we don't fetch on every keystroke. Reset to page 1
  // whenever the active search term changes.
  useEffect(() => {
    const handle = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 300)
    return () => clearTimeout(handle)
  }, [searchInput])

  useEffect(() => {
    let cancelled = false
    const params = new URLSearchParams({
      sort_by: sortField,
      sort_dir: sortDir,
      page: String(page),
      page_size: String(PAGE_SIZE),
    })
    if (search) params.set('search', search)

    fetch(`/api/customers?${params.toString()}`)
      .then((r) => {
        if (!r.ok) throw new Error('Failed to fetch customers')
        return r.json() as Promise<CustomerPage>
      })
      .then((data) => {
        if (cancelled) return
        // If this page is now beyond the available results (e.g. after a
        // deletion emptied it), step back to the last valid page.
        const lastPage = Math.max(1, Math.ceil(data.total / PAGE_SIZE))
        if (data.items.length === 0 && page > lastPage) {
          setPage(lastPage)
          return
        }
        dispatch({ type: 'loaded', customers: data.items, total: data.total })
      })
      .catch(() => {
        if (!cancelled) dispatch({ type: 'failed' })
      })
    return () => {
      cancelled = true
    }
  }, [refreshToken, search, sortField, sortDir, page])

  const total = listState.status === 'ok' ? listState.total : 0
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  const handleSort = useCallback(
    (field: SortField) => {
      if (field === sortField) {
        setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
      } else {
        setSortField(field)
        setSortDir('asc')
      }
      setPage(1)
    },
    [sortField],
  )

  const rangeLabel =
    total === 0
      ? '0 customers'
      : `${(page - 1) * PAGE_SIZE + 1}–${Math.min(page * PAGE_SIZE, total)} of ${total}`

  function handleAddChange(field: keyof FormData, value: string) {
    setAddForm((prev) => ({ ...prev, [field]: value }))
  }

  function handleAddSubmit(e: React.FormEvent) {
    e.preventDefault()
    setAddError('')
    const body: Record<string, string> = {
      name: addForm.name,
      email: addForm.email,
    }
    if (addForm.phone) body.phone = addForm.phone
    if (addForm.company) body.company = addForm.company
    if (addForm.address) body.address = addForm.address

    fetch('/api/customers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then((r) => {
        if (!r.ok) throw new Error('Failed to create customer')
        return r.json()
      })
      .then(() => {
        setAddForm(emptyForm)
        triggerRefresh()
      })
      .catch(() => setAddError('Failed to add customer. Please try again.'))
  }

  function startEdit(customer: Customer) {
    setEditError('')
    setEditState({ id: customer.id, data: customerToFormData(customer) })
  }

  function cancelEdit() {
    setEditState(null)
    setEditError('')
  }

  function handleEditChange(field: keyof FormData, value: string) {
    if (!editState) return
    setEditState({ ...editState, data: { ...editState.data, [field]: value } })
  }

  function handleEditSave(customerId: string) {
    if (!editState) return
    setEditError('')
    const body: Record<string, string> = {
      name: editState.data.name,
      email: editState.data.email,
    }
    if (editState.data.phone) body.phone = editState.data.phone
    if (editState.data.company) body.company = editState.data.company
    if (editState.data.address) body.address = editState.data.address

    fetch(`/api/customers/${customerId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
      .then((r) => {
        if (!r.ok) throw new Error('Failed to update customer')
        return r.json()
      })
      .then(() => {
        setEditState(null)
        triggerRefresh()
      })
      .catch(() => setEditError('Failed to save changes. Please try again.'))
  }

  function handleDelete(customerId: string) {
    fetch(`/api/customers/${customerId}`, { method: 'DELETE' })
      .then((r) => {
        if (!r.ok) throw new Error('Failed to delete customer')
        triggerRefresh()
      })
      .catch(() => {
        triggerRefresh()
      })
  }

  return (
    <main className="customers-page">
      <h1>Manage Customers</h1>

      {listState.status === 'loading' && (
        <p className="customers-status">Loading customers…</p>
      )}
      {listState.status === 'error' && (
        <p className="customers-status customers-status--error">
          Failed to load customers. Please refresh.
        </p>
      )}

      {listState.status === 'ok' && (
        <>
          {editError && <p className="customers-form-error">{editError}</p>}

          <div className="customers-toolbar">
            <div className="customers-search">
              <input
                type="search"
                className="customers-search-input"
                placeholder="Search name, email, or company…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                aria-label="Search customers"
              />
            </div>
            <span className="customers-range">{rangeLabel}</span>
          </div>

          <div className="customers-table-wrapper">
            <table className="customers-table">
              <thead>
                <tr>
                  <SortableHeader
                    label="Name"
                    field="name"
                    activeField={sortField}
                    dir={sortDir}
                    onSort={handleSort}
                  />
                  <SortableHeader
                    label="Email"
                    field="email"
                    activeField={sortField}
                    dir={sortDir}
                    onSort={handleSort}
                  />
                  <th>Phone</th>
                  <SortableHeader
                    label="Company"
                    field="company"
                    activeField={sortField}
                    dir={sortDir}
                    onSort={handleSort}
                  />
                  <th>Address</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {listState.customers.length === 0 && (
                  <tr>
                    <td colSpan={6} className="customers-empty">
                      {search
                        ? 'No customers match your search.'
                        : 'No customers yet. Add one below.'}
                    </td>
                  </tr>
                )}
                {listState.customers.map((customer) =>
                  editState?.id === customer.id ? (
                    <tr key={customer.id} className="customers-row--editing">
                      <td>
                        <input
                          className="customers-input"
                          value={editState.data.name}
                          onChange={(e) => handleEditChange('name', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          className="customers-input"
                          type="email"
                          value={editState.data.email}
                          onChange={(e) => handleEditChange('email', e.target.value)}
                          required
                        />
                      </td>
                      <td>
                        <input
                          className="customers-input"
                          value={editState.data.phone}
                          onChange={(e) => handleEditChange('phone', e.target.value)}
                        />
                      </td>
                      <td>
                        <input
                          className="customers-input"
                          value={editState.data.company}
                          onChange={(e) => handleEditChange('company', e.target.value)}
                        />
                      </td>
                      <td>
                        <input
                          className="customers-input"
                          value={editState.data.address}
                          onChange={(e) => handleEditChange('address', e.target.value)}
                        />
                      </td>
                      <td className="customers-actions">
                        <button
                          className="customers-btn customers-btn--save"
                          onClick={() => handleEditSave(customer.id)}
                        >
                          Save
                        </button>
                        <button
                          className="customers-btn customers-btn--cancel"
                          onClick={cancelEdit}
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
                  ) : (
                    <tr key={customer.id}>
                      <td>{customer.name}</td>
                      <td>{customer.email}</td>
                      <td>{customer.phone ?? ''}</td>
                      <td>{customer.company ?? ''}</td>
                      <td>{customer.address ?? ''}</td>
                      <td className="customers-actions">
                        <button
                          className="customers-btn customers-btn--edit"
                          onClick={() => startEdit(customer)}
                        >
                          Edit
                        </button>
                        <button
                          className="customers-btn customers-btn--delete"
                          onClick={() => handleDelete(customer.id)}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>

          <div className="customers-pagination">
            <button
              className="customers-btn customers-btn--page"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
            >
              Previous
            </button>
            <span className="customers-page-info">
              Page {page} of {totalPages}
            </span>
            <button
              className="customers-btn customers-btn--page"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              Next
            </button>
          </div>
        </>
      )}

      <section className="customers-add">
        <h2>Add Customer</h2>
        {addError && <p className="customers-form-error">{addError}</p>}
        <form className="customers-form" onSubmit={handleAddSubmit}>
          <div className="customers-form-row">
            <label htmlFor="add-name">Name *</label>
            <input
              id="add-name"
              className="customers-input"
              value={addForm.name}
              onChange={(e) => handleAddChange('name', e.target.value)}
              required
            />
          </div>
          <div className="customers-form-row">
            <label htmlFor="add-email">Email *</label>
            <input
              id="add-email"
              className="customers-input"
              type="email"
              value={addForm.email}
              onChange={(e) => handleAddChange('email', e.target.value)}
              required
            />
          </div>
          <div className="customers-form-row">
            <label htmlFor="add-phone">Phone</label>
            <input
              id="add-phone"
              className="customers-input"
              value={addForm.phone}
              onChange={(e) => handleAddChange('phone', e.target.value)}
            />
          </div>
          <div className="customers-form-row">
            <label htmlFor="add-company">Company</label>
            <input
              id="add-company"
              className="customers-input"
              value={addForm.company}
              onChange={(e) => handleAddChange('company', e.target.value)}
            />
          </div>
          <div className="customers-form-row">
            <label htmlFor="add-address">Address</label>
            <input
              id="add-address"
              className="customers-input"
              value={addForm.address}
              onChange={(e) => handleAddChange('address', e.target.value)}
            />
          </div>
          <button type="submit" className="customers-btn customers-btn--submit">
            Add Customer
          </button>
        </form>
      </section>
    </main>
  )
}

export default Customers
