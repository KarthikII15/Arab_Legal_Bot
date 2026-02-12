# Implementation Plan - Light/Dark Theme & Modern UI Update

This plan outlines the steps to implement a clean, attractive, and user-switchable Light/Dark theme for the Arabic AI Legal Assistant.

## Design Philosophy
- **Simple Yet Attractive**: Focus on clean typography, consistent spacing, and soft shadows. Avoid excessive ornamentation.
- **Theme Support**: Use CSS Variables (`:root` vs `[data-theme='dark']`) for seamless switching.
- **Glassmorphism**: Use subtle transparency and blurs to add depth without clutter.

## User Story
As a user, I want to toggle between a bright, clean Light Mode and a deep, comfortable Dark Mode so that I can work comfortably in any lighting condition. The interface should feel modern and polished.

## Technical Tasks

### 1. State Management (App.js)
- [] Add `theme` state (`'light'` | `'dark'`).
- [] Initialize theme from `localStorage` or system preference.
- [] Effect to update `document.documentElement.setAttribute('data-theme', theme)`.
- [] Pass `toggleTheme` function to `Header` component.

### 2. Header Component (Header.js)
- [] Add a Theme Toggle Button (Sun/Moon icon).
- [] Ensure the button fits cleanly in the header controls.
- [] Use Lucide icons (`Sun`, `Moon`).

### 3. CSS Architecture (App.css)
- [] **Refactor `:root`**: Define all semantic colors for Light Mode.
- [] **Add `[data-theme='dark']`**: Override semantic colors for Dark Mode.
  - Backgrounds: Rich Navy/Slate (`#0f172a`, `#1e293b`).
  - Texts: High contrast white/gray.
  - Borders: Subtle transparency (`rgba(255,255,255,0.1)`).
- [] **Consistency**: Ensure all components use CSS variables (`var(--color-bg-primary)`, etc.) instead of hardcoded hex values.

### 4. UI Refinement
- [] **Simplification**: Remove unnecessary gradients if they clutter the view. Stick to subtle ones.
- [] **Spacing**: Review padding/margins to ensure content breathes.
- [] **Typography**: Ensure font weights and sizes are readable in both modes.

## Verification
- [ ] Verify Light Mode looks clean and professional.
- [ ] Verify Dark Mode is legible and uses the correct palette.
- [ ] Verify the toggle switch works instantly.
- [ ] Verify state persists on reload (optional but good practice).
