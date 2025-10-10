# TERAG Immersive Shell v1.0

## Overview

TERAG Immersive Shell is a 3D interactive interface for the TERAG v5.1 Cognitive System. It provides a visual portal into AI reasoning, displaying cognitive processes through an immersive 3D environment.

## Features

### 1. Welcome Screen
- Animated introduction to TERAG
- Smooth transitions with gradient effects
- User Journey flow: Welcome → Dialogue → Analysis → Reflection

### 2. NeuroSpace (3D Scene)
- **TERAG Core Sphere**: Central pulsating sphere representing the AI core
- **Agent Nodes**: 7 cognitive agents (Planner, Intuit, Critic, Verifier, Curator, Reflector, Meta-Controller)
- **Neural Connections**: Animated lines showing reasoning flow between agents
- **Particle Field**: Background particles creating depth and atmosphere
- **Interactive Camera**: Mouse/touch controls for rotation, zoom, and pan

### 3. Cognitive Console
- Text input for queries
- Voice input support (microphone button)
- Real-time response display
- Sound toggle
- Processing indicators

### 4. Metrics HUD
- **IEI Score**: Information-Ethical Intelligence metric
- **Coherence**: Cognitive coherence measurement
- **Faithfulness**: Response accuracy metric
- Animated gauges with color-coded values
- Connection status indicator
- Auto-updates every 5 seconds

### 5. Reasoning Graph Viewer
- Full-screen 3D visualization of reasoning process
- Shows agent connections and flow
- Interactive controls
- Real-time updates during reasoning

## Tech Stack

- **React 18** + **TypeScript**
- **Three.js** + **React Three Fiber** for 3D graphics
- **@react-three/drei** for 3D helpers
- **Framer Motion** for animations
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Lucide React** for icons

## API Integration

The interface connects to TERAG backend API at `http://localhost:8000` with the following endpoints:

- `POST /reasoning/query` - Submit reasoning queries
- `GET /metrics/live` - Get real-time cognitive metrics
- `GET /graph/state` - Get current reasoning graph
- `POST /voice/query` - Submit voice queries
- `GET /healthz` - Check system health

## Environment Variables

Add to `.env`:
```
VITE_TERAG_API_URL=http://localhost:8000
```

## Usage

1. Navigate to `/immersive` route
2. Click "Begin Dialogue" on welcome screen
3. Enter queries in the Cognitive Console
4. Watch the 3D scene react to reasoning processes
5. Click "View Reasoning" to see detailed agent flow
6. Monitor real-time metrics in the HUD

## Visual Design

### Color Palette
- **Primary Accent**: `#00FFE0` (Cyan)
- **Secondary**: `#0099FF` (Blue)
- **Tertiary**: `#FF00FF` (Magenta)
- **Background**: `#0A0E1A` - `#1A1E2E` (Dark gradient)
- **Text**: `#F0F0F0` (Light gray)

### Animations
- Pulsing core during reasoning
- Synaptic connections between agents
- Smooth camera transitions
- Particle effects
- Animated gauges and metrics

## Performance

- 60 FPS target at 4K resolution
- WebGL 2 rendering
- Optimized particle system
- Lazy loading of routes
- Code splitting

## Browser Support

- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

## Future Enhancements (Roadmap)

### Phase 2
- Enhanced reasoning graph visualization
- Multi-step reasoning traces
- Agent-to-agent communication visualization

### Phase 3
- Full voice integration (Whisper API)
- Text-to-Speech responses
- Emotional response indicators
- Advanced audio feedback

## Components Structure

```
src/
├── components/
│   └── immersive/
│       ├── NeuroSpace.tsx          # Main 3D scene
│       ├── CognitiveConsole.tsx    # Input console
│       ├── MetricsHUD.tsx          # Metrics display
│       ├── ReasoningGraphViewer.tsx # Graph viewer
│       └── WelcomeScreen.tsx       # Welcome screen
├── pages/
│   └── TeragImmersive.tsx          # Main page
└── services/
    └── terag-api.ts                # API integration
```

## Notes

- The interface works in simulation mode if TERAG backend is offline
- Simulated data is used for development and testing
- Voice input requires microphone permissions
- 3D scene auto-rotates when idle

---

**Version**: 1.0.0
**Status**: MVP Ready
**Last Updated**: 2025-10-10
