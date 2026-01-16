# TERAG Immersive Shell v1.1 - Voice Interaction Update

## Overview

TERAG Immersive Shell is a 3D interactive interface for the TERAG v5.1 Cognitive System. It provides a visual portal into AI reasoning, displaying cognitive processes through an immersive 3D environment.

**NEW in v1.1**: Full voice interaction with speech-to-text input and text-to-speech responses. See [VOICE_MODE_README.md](./VOICE_MODE_README.md) for details.

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
- **Voice State Reactions** (NEW v1.1): Core changes color based on voice interaction state

### 3. Cognitive Console
- **Text Mode**: Keyboard input for queries
- **Voice Mode** (NEW v1.1): Full speech interaction
  - Push-to-talk voice recording with MediaRecorder API
  - Automatic speech-to-text transcription via TERAG backend
  - Text-to-speech responses using Web Speech API
  - Visual state indicators (Listening → Thinking → Speaking)
  - Mode toggle button for easy switching
- Real-time response display
- TTS toggle control
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
- Voice state visualization (NEW v1.1)

## Tech Stack

- **React 18** + **TypeScript**
- **Three.js** + **React Three Fiber** for 3D graphics
- **@react-three/drei** for 3D helpers
- **Framer Motion** for animations
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Lucide React** for icons
- **Web Speech API** for TTS (NEW v1.1)
- **MediaRecorder API** for voice recording (NEW v1.1)

## API Integration

The interface connects to TERAG backend API at `http://localhost:8000` with the following endpoints:

- `POST /reasoning/query` - Submit text reasoning queries
- `POST /voice/query` - Submit voice queries (audio/webm)
- `GET /metrics/live` - Get real-time cognitive metrics
- `GET /graph/state` - Get current reasoning graph
- `GET /healthz` - Check system health

## Environment Variables

Add to `.env`:
```
VITE_TERAG_API_URL=http://localhost:8000
```

## Usage

### Basic Usage
1. Navigate to `/immersive` route
2. Click "Begin Dialogue" on welcome screen
3. Enter queries in the Cognitive Console (text or voice)
4. Watch the 3D scene react to reasoning processes
5. Click "View Reasoning" to see detailed agent flow
6. Monitor real-time metrics in the HUD

### Voice Mode Usage (v1.1)
1. Click "Voice Mode" button in Cognitive Console
2. Grant microphone permissions when prompted
3. Click microphone button to start recording
4. Speak your question clearly
5. Click again to stop recording
6. Watch TERAG process and respond with voice
7. Toggle speaker icon to enable/disable TTS

## Visual Design

### Color Palette
- **Primary Accent**: `#00FFE0` (Cyan) - Ready state
- **Secondary**: `#0099FF` (Blue) - Processing
- **Voice Listening**: `#4A9EFF` (Light Blue) - NEW v1.1
- **Voice Processing**: `#FFD700` (Gold) - NEW v1.1
- **Tertiary**: `#FF00FF` (Magenta) - Controller agent
- **Background**: `#0A0E1A` - `#1A1E2E` (Dark gradient)
- **Text**: `#F0F0F0` (Light gray)

### Animations
- Pulsing core during reasoning
- Voice state transitions (NEW v1.1)
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
- Efficient voice processing

## Browser Support

- Chrome 90+
- Edge 90+
- Firefox 88+
- Safari 14+

Voice features require:
- MediaRecorder API (Chrome 47+, Firefox 25+)
- Web Speech API (Chrome 33+, Edge 14+, Safari 14.1+)

## Changelog

### v1.1 - Voice Interaction Update (2025-10-10)
- Full voice mode with speech-to-text
- Text-to-speech responses (Web Speech API)
- Visual voice states (Listening, Thinking, Speaking)
- Voice Mode / Text Mode toggle
- TTS enable/disable control
- Animated core reactions to voice states
- Enhanced Cognitive Console with dual modes
- Voice state indicators in HUD

### v1.0 - Initial Release (2025-10-10)
- 3D NeuroSpace visualization
- Cognitive Console with text input
- Metrics HUD with real-time updates
- Reasoning Graph Viewer
- Welcome Screen with User Journey
- Full TERAG API integration

## Future Enhancements (Roadmap)

### Phase 2 (v1.2)
- Enhanced reasoning graph visualization
- Multi-step reasoning traces
- Agent-to-agent communication visualization
- ElevenLabs API integration for premium TTS
- Voice emotion detection
- Multiple voice personas

### Phase 3 (v1.3)
- Multi-language support
- Voice command shortcuts
- Conversation history playback
- Wake word activation
- Voice-controlled 3D navigation
- Group voice chat support

## Components Structure

```
src/
├── components/
│   └── immersive/
│       ├── NeuroSpace.tsx           # Main 3D scene
│       ├── CognitiveConsole.tsx     # Input console (text + voice)
│       ├── VoiceRecorder.tsx        # Voice recording (NEW v1.1)
│       ├── VoiceOutput.tsx          # TTS engine (NEW v1.1)
│       ├── MetricsHUD.tsx           # Metrics display
│       ├── ReasoningGraphViewer.tsx # Graph viewer
│       └── WelcomeScreen.tsx        # Welcome screen
├── pages/
│   └── TeragImmersive.tsx           # Main page with state management
└── services/
    └── terag-api.ts                 # API integration
```

## Notes

- The interface works in simulation mode if TERAG backend is offline
- Simulated data is used for development and testing
- Voice input requires microphone permissions and HTTPS
- TTS requires browser support for Web Speech API
- 3D scene auto-rotates when idle
- All voice features gracefully degrade if APIs unavailable

## Documentation

- **Voice Mode Guide**: [VOICE_MODE_README.md](./VOICE_MODE_README.md)
- **API Integration**: See `src/services/terag-api.ts`
- **Component Docs**: See inline code comments

---

**Version**: 1.1.0
**Status**: Production Ready
**Last Updated**: 2025-10-10
**License**: MIT
