# InfernoGuard AI — Design System Reference

## 🎨 Color Palette

### Background Colors
```css
--bg-primary:        #050816  /* Main app background */
--bg-secondary:      #0b1220  /* Sidebar, secondary areas */
--bg-card:           #0f1729  /* Card backgrounds */
--bg-card-hover:     #141d30  /* Card hover state */
```

### Fire & Alert Colors
```css
--fire-red:          #ff5e00  /* Critical alerts */
--fire-orange:       #ff7a00  /* Fire detections */
--fire-yellow:       #ffb84d  /* Warning states */
```

### Tech & Primary Colors
```css
--primary-cyan:      #00d4ff  /* Primary brand color */
--primary-blue:      #0066ff  /* Secondary brand */
--primary-teal:      #00ffcc  /* Success states */
```

### Status Colors
```css
--status-success:    #00ffcc  /* Online, active, success */
--status-warning:    #ffb84d  /* Warning, medium priority */
--status-danger:     #ff5e00  /* Danger, critical */
--status-info:       #00d4ff  /* Info, neutral */
```

### Text Colors
```css
--text-primary:      #ffffff  /* Main text */
--text-secondary:    #9ca3af  /* Secondary text */
--text-muted:        #6b7280  /* Muted text, labels */
```

### Border Colors
```css
--border-subtle:     rgba(0, 212, 255, 0.15)  /* Light borders */
--border-medium:     rgba(0, 212, 255, 0.25)  /* Medium borders */
--border-strong:     rgba(0, 212, 255, 0.40)  /* Strong borders */
```

## 📝 Typography

### Font Families
```css
--font-primary:      'Inter', 'Segoe UI', system-ui, sans-serif
--font-mono:         'JetBrains Mono', 'Consolas', monospace
```

### Font Sizes
```css
--font-h1:           36px  /* Page titles */
--font-h2:           28px  /* Section titles */
--font-h3:           22px  /* Subsection titles */
--font-body:         15px  /* Body text */
--font-label:        13px  /* Labels, small text */
--font-small:        12px  /* Very small text */
```

### Font Weights
- 300: Light
- 400: Regular
- 500: Medium
- 600: Semi-bold
- 700: Bold
- 800: Extra-bold
- 900: Black

## 📏 Spacing System

```css
--space-xs:          0.25rem  /* 4px */
--space-sm:          0.5rem   /* 8px */
--space-md:          1rem     /* 16px */
--space-lg:          1.5rem   /* 24px */
--space-xl:          2rem     /* 32px */
--space-2xl:         3rem     /* 48px */
```

## 🔲 Border Radius

```css
--radius-sm:         6px   /* Small elements */
--radius-md:         10px  /* Medium elements */
--radius-lg:         14px  /* Large cards */
--radius-xl:         18px  /* Hero sections */
```

## 🎭 Shadows

```css
--shadow-sm:         0 2px 8px rgba(0, 0, 0, 0.15)
--shadow-md:         0 4px 16px rgba(0, 0, 0, 0.25)
--shadow-lg:         0 8px 32px rgba(0, 0, 0, 0.35)
```

## ⚡ Transitions

```css
--transition-fast:   0.15s cubic-bezier(0.4, 0, 0.2, 1)
--transition-med:    0.25s cubic-bezier(0.4, 0, 0.2, 1)
```

## 🧩 Component Classes

### Cards
```html
<div class="ig-card">Standard card</div>
<div class="ig-card ig-card-sm">Small card</div>
<div class="ig-card ig-card-fire">Fire-themed card</div>
```

### Metric Cards
```html
<div class="ig-metric-card">
  <div class="ig-metric-value">42</div>
  <div class="ig-metric-label">Total Incidents</div>
</div>

<div class="ig-metric-card fire">
  <div class="ig-metric-value">12</div>
  <div class="ig-metric-label">Fire Detections</div>
</div>
```

### Badges
```html
<span class="ig-badge fire">🔥 FIRE</span>
<span class="ig-badge smoke">💨 SMOKE</span>
<span class="ig-badge online">● ONLINE</span>
<span class="ig-badge warning">⚠ WARNING</span>
```

### Status Dots
```html
<span class="ig-status-dot active"></span>
<span class="ig-status-dot warning"></span>
<span class="ig-status-dot danger"></span>
<span class="ig-status-dot inactive"></span>
```

### Buttons
```html
<!-- Primary button (default) -->
<div class="stButton">
  <button>Primary Action</button>
</div>

<!-- Fire/Danger button -->
<div class="ig-btn-fire">
  <button>Danger Action</button>
</div>

<!-- Ghost button -->
<div class="ig-btn-ghost">
  <button>Secondary Action</button>
</div>
```

### Hero Sections
```html
<div class="ig-hero">
  <h1 class="ig-hero-title">Page Title</h1>
  <p class="ig-hero-subtitle">Page description</p>
</div>
```

### Section Titles
```html
<p class="ig-section-title">⚡ Section Name</p>
```

### Dividers
```html
<div class="ig-divider"></div>
<div class="ig-divider-subtle"></div>
```

### Typography Utilities
```html
<span class="ig-mono">Monospace text</span>
<span class="ig-label">Label text</span>
<span class="ig-caption">Caption text</span>
<span class="ig-highlight">Highlighted text</span>
<span class="ig-highlight-fire">Fire highlighted text</span>
```

### Severity Classes
```html
<span class="ig-severity-high">Critical</span>
<span class="ig-severity-medium">Medium</span>
<span class="ig-severity-low">Low</span>
```

## 🎬 Animations

### Available Animations
```css
.ig-animate-fadeInUp  /* Fade in from bottom */
.ig-delay-1           /* 0.05s delay */
.ig-delay-2           /* 0.10s delay */
.ig-delay-3           /* 0.15s delay */
.ig-delay-4           /* 0.20s delay */
```

### Keyframes
- `pulse-active`: Pulsing effect for status indicators
- `pulse-fire`: Fire alert pulsing
- `scanLine`: Scanning line animation
- `fadeInUp`: Fade in from bottom
- `shimmer`: Loading shimmer effect
- `radar-pulse`: Radar ring expansion

## 📱 Responsive Breakpoints

```css
@media (max-width: 1200px) { /* Tablet landscape */ }
@media (max-width: 768px)  { /* Mobile */ }
```

## 🎯 Usage Guidelines

### DO ✅
- Use CSS variables for colors
- Apply consistent spacing
- Use provided component classes
- Follow the typography scale
- Maintain hover states
- Keep animations subtle

### DON'T ❌
- Hardcode colors
- Mix spacing values
- Create custom shadows
- Use random font sizes
- Remove transitions
- Add excessive animations

## 🔧 Customization

To customize the theme, modify the CSS variables in `:root`:

```css
:root {
  --primary-cyan: #your-color;
  --font-body: 16px;
  /* etc. */
}
```

## 📚 Component Examples

### Analytics Card
```html
<div class="ig-predictive-card">
  <div class="ig-predictive-icon">🎯</div>
  <div class="ig-predictive-label">Risk Level</div>
  <div class="ig-predictive-value ig-risk-high">HIGH</div>
  <div class="ig-predictive-sub">Based on 24h activity</div>
</div>
```

### Incident Card
```html
<div class="ig-incident-details">
  <div class="ig-incident-detail-row">
    <span class="ig-incident-detail-label">Type</span>
    <span class="ig-badge fire">🔥 FIRE</span>
  </div>
</div>
```

### Profile Hero
```html
<div class="ig-profile-hero">
  <div class="ig-profile-hero-left">
    <div class="ig-profile-avatar">JD</div>
    <div class="ig-profile-info">
      <div class="ig-profile-name">John Doe</div>
      <div class="ig-profile-role-badge">Operator</div>
    </div>
  </div>
</div>
```

## 🎨 Color Usage Guide

| Element | Color Variable | Use Case |
|---------|---------------|----------|
| Page background | `--bg-primary` | Main app background |
| Cards | `--bg-card` | All card components |
| Primary actions | `--primary-cyan` | Buttons, links, highlights |
| Fire alerts | `--fire-red` | Critical fire detections |
| Success states | `--status-success` | Online, active, success |
| Body text | `--text-primary` | Main readable text |
| Labels | `--text-secondary` | Form labels, captions |
| Borders | `--border-subtle` | Card borders, dividers |

## 📖 Best Practices

1. **Consistency**: Use the same component for the same purpose
2. **Hierarchy**: Follow the typography scale
3. **Spacing**: Use the spacing system
4. **Colors**: Stick to the palette
5. **Accessibility**: Maintain contrast ratios
6. **Performance**: Minimize animations
7. **Responsiveness**: Test on multiple screen sizes

---

**Version**: 3.0  
**Last Updated**: 2025  
**Maintained by**: InfernoGuard AI Team
