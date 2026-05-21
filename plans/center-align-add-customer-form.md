> Source: issue 27
> Notion page: 3679ebdf202a80409968f39f2577f334

# Plan: Center-Align Add Customer Form

## Objective
Center-align the "Add Customer" section (heading + form) in the Manage Customers tab so they appear as a visual unit centered on the page.

## Change
- **File**: `frontend/src/pages/Customers.css`
- **Rule**: `.customers-add`
- **Action**: Add `display: flex; flex-direction: column; align-items: center;`

## Current State
The `.customers-add` rule currently only sets `margin-top: 1rem;`. The heading and form render left-aligned by default.

## After Change
```css
.customers-add {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
```

The `.customers-form` already has `max-width: 480px`, so centering the flex container will visually center both the `<h2>` heading and the form within the page.

## Acceptance Criteria
- The "Add Customer" heading is visually centered on the page
- The form (max-width 480px) is centered on the page
- No regressions to the customer list table (separate `.customers-table-wrapper` rule)
- Layout looks correct at desktop and tablet widths
