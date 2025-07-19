# KTMB Shuttle Website Element Guide

This document provides a comprehensive guide for interacting with elements on the KTMB Shuttle website (https://shuttleonline.ktmb.com.my/Home/Shuttle) for web scraping purposes.

## Page Overview

The KTMB Shuttle website is a train booking system for the Shuttle Tebrau service between JB Sentral (Malaysia) and Woodlands CIQ (Singapore).

## Main Form Elements

### 1. Direction Selection

**Element Type**: Direction Swap Button
- **Selector**: `i` (second instance) or `[ref=e30]`
- **Behavior**: Clicking this button swaps the origin and destination
- **Default State**: 
  - Origin: "JB SENTRAL" 
  - Destination: "WOODLANDS CIQ"
- **After Click**:
  - Origin: "WOODLANDS CIQ"
  - Destination: "JB SENTRAL"

**Element Type**: Origin Textbox
- **Selector**: `[ref=e29]` or textbox containing origin
- **Current Value**: "JB SENTRAL" (default)
- **Behavior**: Read-only field, value changes when direction is swapped

**Element Type**: Destination Textbox  
- **Selector**: `[ref=e33]` or textbox containing destination
- **Current Value**: "WOODLANDS CIQ" (default)
- **Behavior**: Read-only field, value changes when direction is swapped

### 2. Date Selection

**Element Type**: Departure Date Field
- **Selector**: `[ref=e38]` or `input[name="Depart"]`
- **Behavior**: Clicking opens a date picker calendar
- **Date Picker Elements**:
  - Month dropdown: `[ref=e108]` (disabled, shows current month)
  - Year dropdown: `[ref=e122]` (options: 2025, 2026)
  - Navigation buttons: `[ref=e126]` (previous), `[ref=e128]` (next)
  - Calendar grid: Days 1-31 in `[ref=e138]` through `[ref=e173]`
- **Validation**: Required field - shows "Please select departing date." if empty

**Element Type**: Return Date Field
- **Selector**: `[ref=e41]` or `input[name="Return"]`
- **Behavior**: Clicking opens a date picker calendar (same structure as departure)
- **Note**: Optional field for round-trip bookings

### 3. Passenger Selection

**Element Type**: Passenger Dropdown
- **Selector**: `[ref=e45]` or `#PassengerCount`
- **Options**:
  - "1 Pax" (default selected)
  - "2 Pax"
  - "3 Pax" 
  - "4 Pax"
  - "5 Pax"
  - "6 Pax"

### 4. Search Button

**Element Type**: Search Button
- **Selector**: `[ref=e53]` or `button[name="SEARCH"]`
- **Behavior**: Submits the form and searches for available trains
- **Validation**: Requires departure date to be selected

## Navigation Elements

### Main Navigation Menu
- **ETS/INTERCITY**: `[ref=e8]` - Link to ETS/Intercity booking
- **KOMUTER**: `[ref=e10]` - Button for Komuter service
- **SHUTTLE TEBRAU**: `[ref=e12]` - Current page (active)
- **RAIL PASS**: `[ref=e14]` - Button for rail pass
- **MYRAILTIME**: `[ref=e16]` - Link to timetable search

### User Account
- **Login/Sign up**: `[ref=e19]` - Link to account login page

## Form Validation

The website includes client-side validation:
- **Departure Date**: Required field
- **Error Message**: "Please select departing date." appears as tooltip `[ref=e174]`

## Expected Search Results

After successful search submission, the page should display:
- Train list table (expected selector: `#tblTrainList` based on current scraper code)
- Available timings and seat availability information

## Technical Notes

### Page Structure
- The page uses a responsive design
- Form elements are contained within the main booking form area
- Date picker appears as an overlay when date fields are clicked
- Direction swap is handled by JavaScript without page reload

### Recommended Scraping Approach
1. **Direction**: Use the swap button to toggle between directions
2. **Dates**: Fill date fields directly or use date picker interaction
3. **Passengers**: Select from dropdown options
4. **Search**: Click search button and wait for results table
5. **Results**: Parse the train list table for timing and availability data

### Error Handling
- Always check for validation messages before proceeding
- Wait for elements to be visible before interaction
- Handle cases where no trains are available for selected criteria

## CSS Selectors Summary

```css
/* Direction swap */
i:nth-child(2) /* or the second i element */

/* Date fields */
input[name="Depart"] /* Departure date */
input[name="Return"] /* Return date */

/* Passenger dropdown */
#PassengerCount

/* Search button */
button[name="SEARCH"]

/* Validation message */
.tooltip /* or similar class for error messages */

/* Expected results table */
#tblTrainList
```

## Playwright Code Examples

```javascript
// Swap direction
await page.locator('i').nth(1).click();

// Fill departure date
await page.getByRole('textbox', { name: 'Depart' }).fill('16/07/2025');

// Select passengers
await page.locator('#PassengerCount').selectOption('2 Pax');

// Click search
await page.getByRole('button', { name: 'SEARCH' }).click();

// Wait for results
await page.waitForSelector('#tblTrainList');
```
