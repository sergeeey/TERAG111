# Changelog

All notable changes to TERAG Immersive Shell will be documented in this file.

## [1.1.0] - 2025-10-10

### Added - Voice Mode & Russian Language

#### Voice Interaction (v1.1)
- **Full Voice Mode** with speech-to-text and text-to-speech
- **VoiceRecorder Component**: MediaRecorder API integration for audio capture
  - Push-to-talk interface with visual feedback
  - Audio optimization: echo cancellation, noise suppression, 44.1kHz sampling
  - Recording indicators with animated states
- **VoiceOutput Component**: Web Speech API for TTS
  - Automatic voice selection (Google, Microsoft, Yandex)
  - Configurable parameters: rate, pitch, volume
  - Speaking indicators synchronized with audio playback
- **Voice States Visualization**: 3D core reacts to voice interactions
  - Listening: Blue core (#4A9EFF)
  - Processing: Gold core (#FFD700)
  - Speaking: White glow effect
- **Enhanced CognitiveConsole**: Toggle between Text Mode and Voice Mode
- **Voice Mode Toggle**: Easy switching with persistent settings

#### Russian Language Support
- **Complete i18n System**: LanguageContext with translation management
- **LanguageSelector Component**: EN/RU toggle button
- **Full UI Translation**: All interface elements translated to Russian
  - Welcome Screen: "Добро пожаловать в TERAG"
  - Cognitive Console: "Спросите TERAG о чём угодно..."
  - Metrics HUD: "Когнитивные Метрики", "Когерентность"
  - Agent Names: "Планировщик", "Интуитор", "Критик", etc.
- **Russian TTS Support**: Automatic Russian voice selection
  - Google Russian voices
  - Microsoft Irina/Pavel
  - Yandex voices (when available)
- **Persistent Language Settings**: Choice saved to localStorage
- **Document Root Language**: Sets `<html lang="ru">` attribute

#### Documentation
- **VOICE_MODE_README.md**: Complete voice mode guide
- **RUSSIAN_LANGUAGE_README.md**: Bilingual documentation (EN/RU)
- **TESTING_VOICE_MODE.md**: Comprehensive testing checklist
- **Updated TERAG_IMMERSIVE_README.md**: v1.1 features and changelog

### Changed
- **NeuroSpace.tsx**: Added voice state props and color transitions
- **ReasoningGraphViewer.tsx**: Voice state propagation
- **TeragImmersive.tsx**: Voice state management and language selector
- **App.tsx**: Added LanguageProvider wrapper
- **WelcomeScreen.tsx**: Full i18n integration with language selector

### Technical
- **Build Size**: TeragImmersive bundle ~48.84 kB (14.37 kB gzipped)
- **New Dependencies**: None (uses native Web APIs)
- **Browser Support**:
  - MediaRecorder API: Chrome 47+, Firefox 25+, Edge 79+
  - Web Speech API: Chrome 33+, Edge 14+, Safari 14.1+
- **Performance**: 60 FPS maintained with voice processing

### Files Added
```
src/
├── components/
│   ├── immersive/
│   │   ├── VoiceRecorder.tsx          (NEW)
│   │   ├── VoiceOutput.tsx            (NEW)
│   │   └── WelcomeScreen.old.tsx      (backup)
│   └── ui/
│       └── LanguageSelector.tsx       (NEW)
├── i18n/
│   ├── LanguageContext.tsx            (NEW)
│   └── translations.ts                (NEW)

docs/
├── VOICE_MODE_README.md               (NEW)
├── RUSSIAN_LANGUAGE_README.md         (NEW)
└── TESTING_VOICE_MODE.md              (NEW)
```

### Files Modified
```
src/
├── App.tsx                            (LanguageProvider added)
├── components/immersive/
│   ├── CognitiveConsole.tsx           (Voice Mode integration)
│   ├── NeuroSpace.tsx                 (Voice states)
│   ├── ReasoningGraphViewer.tsx       (Voice state prop)
│   ├── VoiceOutput.tsx                (Russian TTS)
│   └── WelcomeScreen.tsx              (i18n)
└── pages/
    └── TeragImmersive.tsx             (Voice state + LanguageSelector)
```

---

## [1.0.0] - 2025-10-10

### Added - Initial Release

#### Core Features
- **3D NeuroSpace Visualization**
  - TERAG Core Sphere with pulsating animation
  - 7 Cognitive Agents (Planner, Intuit, Critic, Verifier, Curator, Reflector, Meta-Controller)
  - Neural connections between agents
  - Particle field background
  - Interactive camera controls (OrbitControls)

- **Cognitive Console**
  - Text input for queries
  - Real-time response display
  - Processing indicators
  - Sound toggle

- **Metrics HUD**
  - IEI Score gauge with animation
  - Coherence measurement
  - Faithfulness metric
  - Color-coded values (green → red)
  - Connection status indicator
  - Auto-refresh every 5 seconds

- **Reasoning Graph Viewer**
  - Full-screen 3D visualization
  - Agent connections and flow
  - Interactive controls
  - Real-time updates during reasoning

- **Welcome Screen**
  - Animated introduction
  - Smooth text transitions
  - User Journey flow

#### API Integration
- **TERAG Backend Connection**: `http://localhost:8000`
- **Endpoints**:
  - `POST /reasoning/query` - Text queries
  - `GET /metrics/live` - Real-time metrics
  - `GET /graph/state` - Reasoning graph
  - `GET /healthz` - Health check
- **Simulation Mode**: Fallback when backend offline

#### Tech Stack
- React 18 + TypeScript
- Three.js + React Three Fiber
- @react-three/drei
- Framer Motion
- Tailwind CSS
- Lucide React icons

#### Design
- **Color Palette**: Cyan (#00FFE0), Blue (#0099FF), Magenta (#FF00FF)
- **Dark Theme**: Gradient background (#0A0E1A → #1A1E2E)
- **60 FPS Performance**: WebGL 2 rendering
- **Responsive**: Desktop-first design

#### Documentation
- **TERAG_IMMERSIVE_README.md**: Complete project documentation
- **Component Structure**: Modular architecture
- **API Documentation**: Inline code comments

---

## Upcoming Features

### [1.2.0] - Planned
- Enhanced reasoning graph visualization
- Multi-step reasoning traces
- Agent-to-agent communication visualization
- ElevenLabs API integration for premium TTS
- Voice emotion detection
- Multiple voice personas

### [1.3.0] - Planned
- Multi-language support (Ukrainian, Belarusian)
- Voice command shortcuts
- Conversation history playback
- Wake word activation
- Voice-controlled 3D navigation
- Group voice chat support

---

## Release Notes

### How to Upgrade

#### From v1.0 to v1.1
```bash
git pull origin main
npm install  # No new dependencies
npm run build
```

The upgrade is seamless - all v1.0 features remain intact with new voice and language capabilities added on top.

### Breaking Changes
- None. v1.1 is fully backward compatible with v1.0

### Migration Guide
No migration needed. Existing integrations continue to work.

---

## Links

- **Repository**: https://github.com/sergeeey/TERAG111.git
- **Documentation**: See README files in project root
- **Issues**: GitHub Issues
- **License**: MIT
