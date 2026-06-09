# InfernoGuard AI — UI Testing Checklist

## 🧪 Visual Testing Checklist

### ✅ Global Elements

- [ ] **Font Consistency**
  - [ ] All headings use correct sizes (H1: 36px, H2: 28px, H3: 22px)
  - [ ] Body text is 15px and readable
  - [ ] Labels are 13px and visible
  - [ ] No tiny unreadable text anywhere
  - [ ] All text uses Inter font family

- [ ] **Color Consistency**
  - [ ] Background is #050816 (dark blue)
  - [ ] Cards are #0f1729 (lighter blue)
  - [ ] Primary cyan (#00d4ff) used consistently
  - [ ] Fire red (#ff5e00) for alerts
  - [ ] No random purple or mismatched colors
  - [ ] All text is readable (good contrast)

- [ ] **Spacing**
  - [ ] No excessive empty space at top of pages
  - [ ] Consistent padding in all cards
  - [ ] Proper margins between sections
  - [ ] No giant gaps between elements
  - [ ] Compact but not cramped

### ✅ Sidebar

- [ ] **Layout**
  - [ ] Width is 280px
  - [ ] Logo section at top is properly styled
  - [ ] User profile card displays correctly
  - [ ] AI status widget shows properly
  - [ ] Navigation links are aligned

- [ ] **Navigation**
  - [ ] All page links are visible
  - [ ] Hover effect works (cyan background)
  - [ ] Active page is highlighted
  - [ ] Icons and text are aligned
  - [ ] Smooth transitions on hover

- [ ] **User Section**
  - [ ] Avatar displays with initials
  - [ ] Username is visible
  - [ ] Role badge shows correctly
  - [ ] Stats display properly
  - [ ] Online indicator pulses

- [ ] **Logout**
  - [ ] Logout button at bottom
  - [ ] Proper styling (fire theme)
  - [ ] Hover effect works
  - [ ] Session hint visible

### ✅ Login Page

- [ ] **Layout**
  - [ ] Split-screen layout (left brand, right auth)
  - [ ] Both columns are properly sized
  - [ ] Vertically centered content
  - [ ] No HTML rendering as text
  - [ ] No escaped characters visible

- [ ] **Brand Panel (Left)**
  - [ ] Logo displays correctly
  - [ ] Headline is readable
  - [ ] Feature cards show properly
  - [ ] Stats display at bottom
  - [ ] Trust badges visible

- [ ] **Auth Panel (Right)**
  - [ ] Card is properly contained
  - [ ] Tabs work (Sign In / Create Account)
  - [ ] Form inputs are styled
  - [ ] Buttons are visible
  - [ ] Footer shows at bottom

### ✅ Dashboard Page

- [ ] **Hero Banner**
  - [ ] Contained in proper card
  - [ ] System status displays
  - [ ] Clock shows correctly
  - [ ] No floating elements
  - [ ] Gradient background visible

- [ ] **AI Status Cards (4 cards)**
  - [ ] All 4 cards display in row
  - [ ] Icons visible
  - [ ] Values are readable
  - [ ] Labels are uppercase
  - [ ] Hover effects work

- [ ] **Monitoring Summary (4 metrics)**
  - [ ] Metric cards aligned
  - [ ] Values are large and readable
  - [ ] Labels are visible
  - [ ] Gradient underlines show
  - [ ] Hover lift effect works

- [ ] **AI Engine Cards (2x2 grid)**
  - [ ] 4 cards in 2 rows
  - [ ] Icons display
  - [ ] Titles are bold
  - [ ] Descriptions readable
  - [ ] Borders visible

- [ ] **Enterprise Metrics (8 cards)**
  - [ ] 2 rows of 4 cards each
  - [ ] All values visible
  - [ ] Labels readable
  - [ ] Consistent sizing
  - [ ] Gradient bars at bottom

- [ ] **Charts**
  - [ ] Heatmap displays correctly
  - [ ] Timeline chart shows
  - [ ] AI metrics bar chart visible
  - [ ] Proper spacing between charts
  - [ ] Labels are readable

- [ ] **Incident Feed**
  - [ ] Recent incidents display
  - [ ] Badges show correctly
  - [ ] Timestamps visible
  - [ ] Confidence scores readable
  - [ ] Empty state if no data

- [ ] **AI Recommendations**
  - [ ] Section header visible
  - [ ] Recommendation cards display
  - [ ] Priority badges show
  - [ ] Text is readable
  - [ ] Proper spacing

### ✅ Live Detection Page

- [ ] **Hero Header**
  - [ ] Contained in card
  - [ ] Title visible
  - [ ] Status badge shows
  - [ ] Timestamp displays
  - [ ] No floating elements

- [ ] **Status Cards (4 cards)**
  - [ ] Detection status shows
  - [ ] FPS displays
  - [ ] Detections today visible
  - [ ] Threat level shows
  - [ ] Status dots animate

- [ ] **Controls Section**
  - [ ] Source selector visible
  - [ ] Input fields styled
  - [ ] Start button (fire theme)
  - [ ] Stop button (ghost theme)
  - [ ] Proper spacing

- [ ] **Video Feed**
  - [ ] Container properly sized
  - [ ] Corner brackets visible
  - [ ] Scan line animates
  - [ ] No excessive empty space
  - [ ] FPS overlay shows

- [ ] **Side Panel**
  - [ ] Last detection displays
  - [ ] Severity assessment shows
  - [ ] AI response visible
  - [ ] Screenshot displays
  - [ ] Proper card styling

- [ ] **Notifications**
  - [ ] Live feed displays
  - [ ] Notification items styled
  - [ ] Badges show correctly
  - [ ] Timestamps visible
  - [ ] Scrollable if many

### ✅ Analytics Page

- [ ] **Header**
  - [ ] Contained in card
  - [ ] Title with gradient
  - [ ] Safety score displays
  - [ ] Badge visible
  - [ ] Subtitle readable

- [ ] **Predictive Cards (4 cards)**
  - [ ] All 4 cards in row
  - [ ] Icons display
  - [ ] Values are large
  - [ ] Labels visible
  - [ ] Color coding correct

- [ ] **Charts Row 1**
  - [ ] Safety gauge displays
  - [ ] Gauge is visible (not tiny)
  - [ ] Risk heatmap shows
  - [ ] Proper sizing
  - [ ] Labels readable

- [ ] **Charts Row 2**
  - [ ] Confidence trend displays
  - [ ] Detection velocity shows
  - [ ] Both charts sized properly
  - [ ] Legends visible
  - [ ] Axes labeled

- [ ] **Charts Row 3**
  - [ ] Pie chart displays
  - [ ] Frequency chart shows
  - [ ] Colors are distinct
  - [ ] Labels readable
  - [ ] Proper spacing

- [ ] **Charts Row 4**
  - [ ] Weekly trend displays
  - [ ] Monthly trend shows
  - [ ] Both charts aligned
  - [ ] Data visible
  - [ ] Proper sizing

- [ ] **Recommendations**
  - [ ] Section header visible
  - [ ] Cards display properly
  - [ ] Priority badges show
  - [ ] Text readable
  - [ ] Hover effects work

### ✅ Incident History Page

- [ ] **Header**
  - [ ] Contained in card
  - [ ] Title visible
  - [ ] Badge shows
  - [ ] Subtitle readable
  - [ ] No floating elements

- [ ] **Stat Cards (4 cards)**
  - [ ] Total incidents shows
  - [ ] Fire count displays
  - [ ] Smoke count visible
  - [ ] Avg confidence shows
  - [ ] Gradient values

- [ ] **Search & Filters**
  - [ ] Search bar styled
  - [ ] Filter chips display
  - [ ] Active filter highlighted
  - [ ] Proper spacing
  - [ ] Buttons aligned

- [ ] **Export Buttons**
  - [ ] CSV button visible
  - [ ] JSON button visible
  - [ ] Proper alignment
  - [ ] Hover effects work
  - [ ] Icons display

- [ ] **Incident Cards**
  - [ ] Expanders display
  - [ ] Badges show correctly
  - [ ] Confidence visible
  - [ ] Timestamps readable
  - [ ] Proper spacing

- [ ] **Incident Details**
  - [ ] Details table displays
  - [ ] Screenshot shows
  - [ ] AI summary visible
  - [ ] Severity badge shows
  - [ ] Proper layout

- [ ] **Pagination**
  - [ ] Page info displays
  - [ ] Page selector works
  - [ ] Proper alignment
  - [ ] Text readable
  - [ ] No overflow

- [ ] **Empty State**
  - [ ] Shows when no data
  - [ ] Icon displays
  - [ ] Message readable
  - [ ] Proper styling
  - [ ] Centered layout

### ✅ Settings Page

- [ ] **Header**
  - [ ] Contained in card
  - [ ] Title visible
  - [ ] Badge shows
  - [ ] Subtitle readable
  - [ ] No floating elements

- [ ] **Profile Hero**
  - [ ] Avatar displays
  - [ ] Name visible
  - [ ] Role badge shows
  - [ ] Email displays
  - [ ] Stats visible (3 stats)
  - [ ] Online indicator pulses
  - [ ] Proper layout

- [ ] **Edit Toggle**
  - [ ] Toggle displays
  - [ ] Works correctly
  - [ ] Proper styling
  - [ ] Label visible
  - [ ] State changes

- [ ] **Tabs**
  - [ ] All 5 tabs visible
  - [ ] Active tab highlighted
  - [ ] Hover effects work
  - [ ] Icons display
  - [ ] Proper spacing

- [ ] **Profile Tab**
  - [ ] Section header shows
  - [ ] Input fields styled
  - [ ] Labels visible
  - [ ] 2-column layout
  - [ ] Save button displays

- [ ] **Security Tab**
  - [ ] Info card displays
  - [ ] Security rows visible
  - [ ] Status badges show
  - [ ] Password form styled
  - [ ] Inputs visible

- [ ] **Alerts Tab**
  - [ ] Threshold slider works
  - [ ] Alert rows display
  - [ ] Icons visible
  - [ ] Toggles work
  - [ ] Descriptions readable
  - [ ] Save button shows

- [ ] **Integrations Tab**
  - [ ] Integration cards display
  - [ ] Status indicators show
  - [ ] Forms are styled
  - [ ] Input fields visible
  - [ ] Save buttons work
  - [ ] Proper spacing

- [ ] **Appearance Tab**
  - [ ] Appearance card displays
  - [ ] Settings rows visible
  - [ ] Color swatches show
  - [ ] Values readable
  - [ ] Proper layout

### ✅ Responsive Design

- [ ] **Desktop (1920px)**
  - [ ] All elements visible
  - [ ] Proper spacing
  - [ ] No overflow
  - [ ] Cards aligned
  - [ ] Text readable

- [ ] **Laptop (1366px)**
  - [ ] Layout adapts
  - [ ] No horizontal scroll
  - [ ] Cards resize properly
  - [ ] Text still readable
  - [ ] Sidebar visible

- [ ] **Tablet (768px)**
  - [ ] Mobile-friendly layout
  - [ ] Sidebar collapses
  - [ ] Cards stack vertically
  - [ ] Text scales down
  - [ ] Touch-friendly buttons

### ✅ Interactions

- [ ] **Hover States**
  - [ ] Cards lift on hover
  - [ ] Buttons change on hover
  - [ ] Links highlight on hover
  - [ ] Smooth transitions
  - [ ] No jarring effects

- [ ] **Click States**
  - [ ] Buttons press down
  - [ ] Links navigate
  - [ ] Toggles switch
  - [ ] Forms submit
  - [ ] Feedback visible

- [ ] **Animations**
  - [ ] Fade-in on load
  - [ ] Pulse animations work
  - [ ] Scan line animates
  - [ ] Smooth transitions
  - [ ] Not excessive

### ✅ Accessibility

- [ ] **Contrast**
  - [ ] Text readable on backgrounds
  - [ ] Buttons have good contrast
  - [ ] Labels are visible
  - [ ] Status indicators clear
  - [ ] WCAG AA compliant

- [ ] **Focus States**
  - [ ] Inputs show focus
  - [ ] Buttons show focus
  - [ ] Links show focus
  - [ ] Keyboard navigable
  - [ ] Visible outlines

- [ ] **Text Size**
  - [ ] Minimum 13px for labels
  - [ ] 15px for body text
  - [ ] Scalable with zoom
  - [ ] No tiny text
  - [ ] Readable at 100%

## 🐛 Known Issues to Check

- [ ] No HTML rendering as plain text
- [ ] No escaped characters (e.g., `&amp;`)
- [ ] No invisible text
- [ ] No broken layouts
- [ ] No overflow issues
- [ ] No missing borders
- [ ] No misaligned elements
- [ ] No excessive spacing
- [ ] No tiny fonts
- [ ] No color mismatches

## ✨ Final Quality Check

- [ ] Professional appearance
- [ ] Consistent design language
- [ ] No visual bugs
- [ ] Smooth interactions
- [ ] Fast performance
- [ ] Mobile-friendly
- [ ] Accessible
- [ ] Production-ready

## 📝 Testing Notes

**Browser Testing:**
- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari (if available)

**Screen Sizes:**
- [ ] 1920x1080 (Desktop)
- [ ] 1366x768 (Laptop)
- [ ] 768x1024 (Tablet)

**Performance:**
- [ ] Page loads quickly
- [ ] Animations are smooth
- [ ] No lag on interactions
- [ ] CSS file size reasonable

---

**Status**: Ready for Testing  
**Version**: 3.0  
**Date**: 2025
