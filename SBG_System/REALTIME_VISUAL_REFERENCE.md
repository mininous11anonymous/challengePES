# 🎨 REAL-TIME MONITORING - VISUAL QUICK REFERENCE

---

## 📱 DASHBOARD CONTROLS

### Button Layout (Top Control Bar)

```
┌─────────────────────────────────────────────────────────────┐
│                       CONTROL BUTTONS                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  [ 📊 Load Real Data ] [ 🔍 Run Analysis ] [ 🔴 START... ]   │
│  [ ⚫ STOP MONITOR ]* [ 📥 Download PDF ] [ 🗑️ Clear ]      │
│                                                               │
│  * Only visible when monitoring is active                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘

Color Scheme:
├─ Blue buttons: Data operations
├─ Red button (🔴): Start monitoring
└─ Dark red button (⚫): Stop monitoring (when active)
```

---

## 🔴 REAL-TIME STATUS CARD

### When Monitoring is INACTIVE (Hidden)

```
Dashboard shows:
- Overall Status card
- Thermal Analysis card
- Acoustic Analysis card
- RUL Prediction card
- Anomaly Detection card
- Batteries List card

No real-time status visible
```

### When Monitoring is ACTIVE (Visible)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                              ┃
┃        🔴 REAL-TIME DATA INGESTION ACTIVE                   ┃
┃                                                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃                                                              ┃
┃  ┌──────────────────┐  ┌──────────────────┐               ┃
┃  │     12,450       │  │        45        │               ┃
┃  │ Data Points      │  │    Analyses      │               ┃
┃  │ Ingested         │  │    Completed     │               ┃
┃  └──────────────────┘  └──────────────────┘               ┃
┃                                                              ┃
┃  ┌──────────────────┐  ┌──────────────────┐               ┃
┃  │      24.5        │  │      510s        │               ┃
┃  │ Points/Second    │  │      Uptime      │               ┃
┃  └──────────────────┘  └──────────────────┘               ┃
┃                                                              ┃
┃  ┌──────────────────┐  ┌──────────────────┐               ┃
┃  │        5         │  │       ●          │               ┃
┃  │   Batteries      │  │     Status:      │               ┃
┃  │   Monitored      │  │      LIVE        │               ┃
┃  └──────────────────┘  └──────────────────┘               ┃
┃                                                              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

Appearance:
├─ Background: Purple gradient
│  ├─ Start: #667eea
│  └─ End: #764ba2
├─ Text color: White
├─ Heading: "🔴 REAL-TIME DATA INGESTION ACTIVE"
├─ Grid: 6 columns (responsive)
├─ Each metric box:
│  ├─ Large value (2em font)
│  ├─ Label below (0.9em font)
│  └─ Center aligned
├─ Status indicator: Blinking ● in green
└─ Update rate: Every 0.5 seconds
```

---

## 🔄 CONTROL FLOW

### Start Monitoring

```
User Action:
  Click [ 🔴 Start Real-Time Monitor ]
           ↓
Visual Feedback:
  ├─ Status card appears (with animation)
  ├─ "🔴 REAL-TIME DATA INGESTION ACTIVE" shows
  ├─ Stop button appears (⚫ STOP MONITOR)
  ├─ Message: "✓ Real-time monitoring ACTIVE"
  └─ Metrics start updating every 0.5 seconds
           ↓
Continuous Updates:
  Every 0.5 seconds:
  ├─ Data Points increment
  ├─ Analyses count increases
  ├─ Rate is calculated
  ├─ Uptime counts up
  ├─ Battery count updates
  └─ Status indicator blinks (● → ◦ → ● → ◦)
```

### Stop Monitoring

```
User Action:
  Click [ ⚫ Stop Monitoring ]
           ↓
Visual Feedback:
  ├─ Status card disappears (with animation)
  ├─ Stop button disappears
  ├─ Start button visible again
  ├─ Message shows final metrics
  │  "✓ Real-time monitoring stopped.
  │   Ingested: 12,450 data points |
  │   Completed: 45 analyses"
  └─ Dashboard returns to normal view
```

---

## 📊 METRICS EXPLAINED

### Data Points Ingested

```
What it shows: Total data points loaded from all agents

Calculation:
├─ Thermal agent data: counts
├─ Acoustic agent data: counts
├─ RUL agent data: counts
├─ Anomaly agent data: counts
└─ Total: sum of all above

Example progression:
├─ Start: 0
├─ 5 sec: 1,250
├─ 10 sec: 2,450
├─ 15 sec: 3,650
└─ 20 sec: 4,850
```

### Analyses Completed

```
What it shows: Number of battery assessments finished

Calculation:
└─ Count of completed analysis batches

Example progression:
├─ Start: 0
├─ 5 sec: 2
├─ 10 sec: 4
├─ 15 sec: 6
└─ 20 sec: 8

(Each batch = 2 batteries analyzed)
```

### Points/Second

```
What it shows: Data ingestion rate in real time

Formula:
└─ data_points_ingested / elapsed_time_seconds

Example:
├─ After 5 sec: 1,250 / 5 = 250 pts/sec
├─ After 10 sec: 2,450 / 10 = 245 pts/sec
├─ After 15 sec: 3,650 / 15 = 243 pts/sec
└─ Stabilizes around: 24.5 pts/sec (depends on data)
```

### Uptime

```
What it shows: How long monitoring has been active

Calculation:
└─ (current_time - start_time) rounded to seconds

Example progression:
├─ Just started: 0s
├─ After 5 seconds: 5s
├─ After 10 seconds: 10s
├─ After 1 minute: 60s
└─ After 5 minutes: 300s
```

### Batteries Monitored

```
What it shows: How many unique batteries are being tracked

Calculation:
└─ Count of unique battery IDs seen

Example progression:
├─ Start: 0 batteries
├─ 5 sec: 2 batteries (TFUDS_050, TFUDS_080)
├─ 10 sec: 3 batteries (added TFUDS_2550)
├─ 15 sec: 4 batteries (added TFUDS_2580)
└─ Final: 5 batteries (added TFUDS_4550)
```

### Status Indicator

```
What it shows: System is actively monitoring in real time

Animation:
├─ Bright: ● (when updating)
├─ Dim: ◦ (between updates)
├─ Pattern: Blinks continuously while active
├─ Color: Green (#4caf50)
└─ Speed: Every 0.5 seconds

Meaning:
├─ Blinking ●: System actively working
├─ Still ●: No updates received (check connection)
└─ Disappeared: Monitoring stopped
```

---

## 🎯 BUTTON STATES

### Start Button (🔴 Start Real-Time Monitor)

```
Appearance:
├─ Label: "🔴 Start Real-Time Monitor"
├─ Background: Blue (#667eea)
├─ Text: White
├─ Style: Normal button
└─ Visible: Always

States:
├─ Normal: Clickable, blue
├─ Hover: Slightly darker blue
├─ Active (pressed): Momentary darker
└─ When monitoring: Still blue (still visible)

Disabled state: Never disabled
```

### Stop Button (⚫ Stop Monitoring)

```
Appearance:
├─ Label: "⚫ Stop Monitoring"
├─ Background: Dark red (#d32f2f)
├─ Text: White
├─ Style: Warning button
└─ Visible: Only when monitoring active

States:
├─ When monitoring: Visible and clickable
├─ When stopped: Hidden (display: none)
├─ Hover: Darker red

Disabled state: Never disabled when visible
```

---

## 💾 LOADING STATES

### During Monitoring Start

```
Timeline:
├─ Click button
├─ ~100ms: Status card appears
├─ ~200ms: First metrics load
├─ ~500ms: First update
└─ Continuous: Updates every 500ms
```

### During Monitoring Stop

```
Timeline:
├─ Click button
├─ ~100ms: Status card fades
├─ ~200ms: Final metrics message shows
├─ ~500ms: Message disappears
└─ Normal: Dashboard ready again
```

---

## 🎨 COLOR SCHEME

### Theme Colors

```
Primary (Gradient):
├─ Start: #667eea (Blueish purple)
└─ End: #764ba2 (Dark purple)

Text:
├─ On gradient: white
├─ On white cards: #333 (dark gray)
└─ On light background: #666 (medium gray)

Buttons:
├─ Normal: #667eea
├─ Hover: #5568d3
├─ Stop button: #d32f2f
└─ Hover (stop): Darker red

Status Indicator:
├─ Color: #4caf50 (green)
├─ Bright: opacity 1.0
└─ Dim: opacity 0.5
```

---

## 📐 RESPONSIVE DESIGN

### Desktop (1200px+)

```
Layout:
├─ Status card: Full width at top
├─ Grid: 6 columns
├─ Buttons: Horizontal row
└─ All metrics visible

Size:
├─ Font: 2em (values)
├─ Font: 0.9em (labels)
└─ Boxes: 150px wide
```

### Tablet (768px - 1199px)

```
Layout:
├─ Status card: Full width
├─ Grid: 3-4 columns (responsive)
├─ Buttons: May wrap
└─ All metrics visible

Size:
├─ Font: 1.5em (values)
├─ Font: 0.85em (labels)
└─ Boxes: Smaller, responsive
```

### Mobile (<768px)

```
Layout:
├─ Status card: Full width
├─ Grid: 2 columns
├─ Buttons: Stack vertically
└─ Scrollable if needed

Size:
├─ Font: 1.2em (values)
├─ Font: 0.8em (labels)
└─ Boxes: Fill width
```

---

## 🔌 DATA FLOW VISUALIZATION

### Real-Time Updates

```
Every 0.5 seconds:

┌─────────────┐
│  Frontend   │
│  Dashboard  │
└──────┬──────┘
       │ GET /api/monitoring/status
       ↓
┌─────────────┐
│   Flask     │
│   Backend   │
└──────┬──────┘
       │ Returns JSON with metrics
       ↓
┌─────────────┐
│  Frontend   │
│  JavaScript │
└──────┬──────┘
       │ Updates DOM elements:
       ├─ #data-points
       ├─ #analysis-count
       ├─ #data-rate
       ├─ #uptime
       ├─ #battery-count
       └─ #status-indicator
       ↓
┌─────────────┐
│  Dashboard  │
│  Metrics    │
│  Updated!   │
└─────────────┘
```

---

## ⚡ PERFORMANCE INDICATORS

### Network Activity

```
Per Update (every 0.5 sec):
├─ Request size: ~200 bytes
├─ Response size: ~500 bytes
└─ Round trip: ~50-100ms
```

### CPU Usage

```
Background thread:
├─ Peak: ~5-10% during data load
├─ Idle: <1% between loads
└─ UI thread: Not blocked
```

### Memory

```
Added overhead:
├─ System metrics dict: ~5 KB
├─ Thread: ~1 MB
└─ Total: <10 MB on top of base
```

---

## 🎯 QUICK REFERENCE

### What Happens When You Click Start

```
1. ✓ Real-time status card appears
2. ✓ Blinking status indicator shows
3. ✓ Metrics begin updating every 500ms
4. ✓ Background thread starts data ingestion
5. ✓ All values update in real-time
6. ✓ Stop button becomes visible
```

### What Happens When You Click Stop

```
1. ✓ Background thread stops
2. ✓ Status card disappears
3. ✓ Stop button hides
4. ✓ Final metrics shown in message
5. ✓ Dashboard returns to normal
6. ✓ All data preserved (no loss)
```

---

**Visual Reference Complete**  
**Status:** ✅ LIVE & OPERATIONAL  
**Date:** December 19, 2025
