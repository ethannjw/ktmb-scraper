# KTMB Shuttle Form Selectors Documentation

This document contains all the CSS selectors and element information for the KTMB Shuttle booking form at `https://shuttleonline.ktmb.com.my/Home/Shuttle`.

## Form Overview

- **Form ID**: `#theForm`
- **Form Class**: `.ticket-search`
- **Action URL**: `https://shuttleonline.ktmb.com.my/ShuttleTrip`
- **Method**: `POST`

## Main Form Fields

### 1. Origin Station (From)
- **Element**: Input field
- **ID**: `#FromStationId`
- **Name**: `FromStationId`
- **Type**: `text`
- **Class**: `.form-control`
- **Readonly**: `true`
- **Default Value**: `JB SENTRAL`
- **Validation**: Required - "Please select origin."

**Selectors**:
```css
#FromStationId
[name="FromStationId"]
.form-control
```

### 2. Destination Station (To)
- **Element**: Input field
- **ID**: `#ToStationId`
- **Name**: `ToStationId`
- **Type**: `text`
- **Class**: `.form-control`
- **Readonly**: `true`
- **Default Value**: `WOODLANDS CIQ`
- **Validation**: Required - "Please select destination."

**Selectors**:
```css
#ToStationId
[name="ToStationId"]
.form-control
```

### 3. Departure Date
- **Element**: Input field
- **ID**: `#OnwardDate`
- **Name**: `OnwardDate`
- **Type**: `text`
- **Placeholder**: `Depart`
- **Class**: `.close-others.form-control.text-center.bg-white`
- **Readonly**: `true`
- **Validation**: Required - "Please select departing date."
- **Data Attributes**: `data-rule-isdate="true"`

**Selectors**:
```css
#OnwardDate
[name="OnwardDate"]
[placeholder="Depart"]
.close-others.form-control.text-center.bg-white
```

### 4. Return Date
- **Element**: Input field
- **ID**: `#ReturnDate`
- **Name**: `ReturnDate`
- **Type**: `text`
- **Placeholder**: `Return`
- **Class**: `.close-others.form-control.text-center.bg-white`
- **Readonly**: `true`
- **Data Attributes**: `data-rule-isdate="true"`

**Selectors**:
```css
#ReturnDate
[name="ReturnDate"]
[placeholder="Return"]
.close-others.form-control.text-center.bg-white
```

### 5. Passenger Count
- **Element**: Select dropdown
- **ID**: `#PassengerCount`
- **Name**: `PassengerCount`
- **Type**: `select-one`
- **Class**: `.form-control.text-center`
- **Required**: `true`
- **Validation**: 
  - Required - "The PassengerCount field is required."
  - Range: 1-99 passengers - "Number of passenger is invalid."

**Selectors**:
```css
#PassengerCount
[name="PassengerCount"]
.form-control.text-center
```

**Options**:
- `1 Pax` (value: "1") - Default selected
- `2 Pax` (value: "2")
- `3 Pax` (value: "3")
- `4 Pax` (value: "4")
- `5 Pax` (value: "5")
- `6 Pax` (value: "6")

### 6. Search Button
- **Element**: Button
- **ID**: `#btnSubmit`
- **Type**: `button`
- **Class**: `.close-others.btn.pull-right.ticket-search-btn.text-dark`
- **Text**: `SEARCH`

**Selectors**:
```css
#btnSubmit
.close-others.btn.pull-right.ticket-search-btn.text-dark
```

## Direction Swap Button

- **Element**: Icon (i)
- **Class**: `.fa.fa-exchange.web-exchange.d-none.d-md-block.mt22`
- **Purpose**: Swaps origin and destination stations

**Selectors**:
```css
i[class*="swap"]
i[class*="exchange"]
.fa.fa-exchange.web-exchange.d-none.d-md-block.mt22
```

## Hidden Fields

### 1. From Station Data
- **ID**: `#FromStationData`
- **Name**: `FromStationData`
- **Type**: `hidden`
- **Validation**: Required - "Data is invalid."

### 2. To Station Data
- **ID**: `#ToStationData`
- **Name**: `ToStationData`
- **Type**: `hidden`
- **Validation**: Required - "Data is invalid."

### 3. Request Verification Token
- **Name**: `__RequestVerificationToken`
- **Type**: `hidden`
- **Purpose**: CSRF protection

### 4. Time Table Index URL
- **ID**: `#TimeTableIndexUrl`
- **Type**: `hidden`
- **Value**: `/TimeTable/Search`

## Validation Error Elements

Error messages appear in elements with the following patterns:
- `#OnwardDate-error` - Departure date validation errors
- `#FromStationId-error` - Origin station validation errors
- `#ToStationId-error` - Destination station validation errors
- `#PassengerCount-error` - Passenger count validation errors

**Selectors**:
```css
[id$="-error"]
.field-validation-error
.validation-error
```

## Expected Results Table Selectors

After a successful search, results typically appear in:
- `#tblTrainList` - Main results table
- `.train-table` - Alternative table class
- `.results-table` - Generic results table
- `[data-testid="train-list"]` - Data attribute selector

## Loading and Error States

### Loading Elements
```css
.loading
.spinner
.loader
[class*="loading"]
[class*="spinner"]
```

### Error Messages
```css
.alert
.error
.validation-error
.field-validation-error
[class*="error"]
```

## Recommended Selector Strategy

### Primary Selectors (Most Reliable)
1. **ID-based selectors** (most stable):
   - `#FromStationId` - Origin
   - `#ToStationId` - Destination
   - `#OnwardDate` - Departure date
   - `#ReturnDate` - Return date
   - `#PassengerCount` - Passenger count
   - `#btnSubmit` - Search button

2. **Name-based selectors** (good fallback):
   - `[name="FromStationId"]`
   - `[name="ToStationId"]`
   - `[name="OnwardDate"]`
   - `[name="ReturnDate"]`
   - `[name="PassengerCount"]`

### Secondary Selectors (Fallbacks)
3. **Placeholder-based selectors**:
   - `[placeholder="Depart"]` - Departure date
   - `[placeholder="Return"]` - Return date

4. **Class-based selectors** (least reliable):
   - `.form-control` - Form inputs
   - `.close-others.form-control.text-center.bg-white` - Date fields

## JavaScript Interaction Notes

### Setting Values
Since most fields are `readonly`, use JavaScript to set values:
```javascript
// Set departure date
document.querySelector('#OnwardDate').value = '15 Aug 2025';
document.querySelector('#OnwardDate').dispatchEvent(new Event('change', { bubbles: true }));

// Set return date
document.querySelector('#ReturnDate').value = '17 Aug 2025';
document.querySelector('#ReturnDate').dispatchEvent(new Event('change', { bubbles: true }));
```

### Direction Swap
```javascript
// Click the exchange button to swap directions
document.querySelector('.fa.fa-exchange').click();
```

### Form Submission
```javascript
// Submit the form
document.querySelector('#btnSubmit').click();
```

## Form Validation Rules

1. **Origin Station**: Required
2. **Destination Station**: Required
3. **Departure Date**: Required, must be valid date
4. **Return Date**: Optional, must be after departure date
5. **Passenger Count**: Required, range 1-99

## Notes for Automation

1. **Readonly Fields**: Most input fields are readonly, requiring JavaScript to set values
2. **Date Format**: Use "DD MMM YYYY" format (e.g., "15 Aug 2025")
3. **Validation**: Form has client-side validation that must be satisfied before submission
4. **CSRF Protection**: Form includes a verification token that must be preserved
5. **Hidden Data**: Origin and destination have encrypted data fields that must be present 