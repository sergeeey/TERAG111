# TERAG Voice Mode v1.1 - Documentation

## Overview

Voice Mode v1.1 adds complete voice interaction capabilities to TERAG Immersive Shell, enabling natural conversation with the AI through speech input and audio responses.

## New Features

### 1. Voice Recording
- **MediaRecorder API integration** for high-quality audio capture
- **Push-to-talk interface** with visual feedback
- **Audio optimization**: Echo cancellation, noise suppression, 44.1kHz sampling
- **Real-time recording indicators** with animated states

### 2. Text-to-Speech (TTS)
- **Web Speech API** for natural voice responses
- **Automatic voice selection** (prefers Google/Microsoft voices)
- **Configurable parameters**: Rate (0.95), pitch (1.0), volume (0.8)
- **Speaking indicators** synchronized with audio playback

### 3. Visual States

The 3D NeuroSpace environment now responds to voice interactions:

| State | Core Color | Behavior | Description |
|-------|-----------|----------|-------------|
| **Idle** | Cyan `#00FFE0` | Normal glow | Ready for input |
| **Listening** | Blue `#4A9EFF` | Soft pulse | Recording user voice |
| **Processing** | Gold `#FFD700` | Active pulse | TERAG reasoning |
| **Speaking** | White glow | Wave effect | TTS audio output |

### 4. Enhanced UI

#### Voice Mode Toggle
- Switch between text and voice input
- Persistent voice settings
- Clear mode indicators

#### Status Display
- Real-time voice state in HUD
- "Listening" → "Thinking" → "Speaking" flow
- Visual feedback in console and scene

#### Recording Controls
- Large microphone button in Voice Mode
- Animated pulse during recording
- Sound effects for record start/end (optional)

## How to Use

### Basic Voice Interaction

1. **Enable Voice Mode**
   - Click "Voice Mode" button in Cognitive Console
   - Grant microphone permissions when prompted

2. **Record Your Query**
   - Click the microphone button
   - Speak your question clearly
   - Click again to stop recording

3. **Receive Response**
   - TERAG processes your query (gold core)
   - Response appears in text
   - TTS automatically speaks the answer

### Advanced Features

#### Toggle TTS Output
- Click speaker icon to enable/disable voice output
- Visual indicator shows speaking state
- Text responses always displayed

#### Text Mode
- Click "Text Mode" to switch back
- Keyboard input returns
- All other features remain active

## Technical Implementation

### Architecture

```
src/
├── components/immersive/
│   ├── VoiceRecorder.tsx      # Audio capture & recording
│   ├── VoiceOutput.tsx        # TTS engine & controls
│   ├── CognitiveConsole.tsx   # Integrated UI (updated)
│   ├── NeuroSpace.tsx         # Voice state visuals (updated)
│   └── ReasoningGraphViewer.tsx # Voice state support (updated)
```

### Voice States Flow

```
IDLE
  ↓ (user clicks mic)
LISTENING (blue core, recording)
  ↓ (user stops recording)
PROCESSING (gold core, API call)
  ↓ (response received)
SPEAKING (white glow, TTS)
  ↓ (speech ends)
IDLE
```

### API Integration

Voice queries are sent to TERAG backend:

```typescript
POST /voice/query
Content-Type: multipart/form-data

Body: {
  audio: Blob (audio/webm)
}

Response: {
  text: string,          // Transcribed query
  response: string,      // TERAG answer
  iei: number,          // Updated IEI score
  coherence?: number,   // Optional metrics
  faithfulness?: number
}
```

## Browser Compatibility

### Required APIs
- **MediaRecorder API**: Chrome 47+, Firefox 25+, Edge 79+
- **Web Speech API**: Chrome 33+, Edge 14+, Safari 14.1+
- **getUserMedia**: All modern browsers

### Fallback Behavior
- Voice Mode button hidden if APIs unavailable
- Text mode always available
- Graceful degradation for TTS

## Performance Considerations

### Audio Processing
- Recording uses WebM format (efficient compression)
- Maximum recording length: 60 seconds (configurable)
- Automatic stream cleanup after recording

### Visual Updates
- Voice state changes trigger minimal re-renders
- 3D scene optimizations for state transitions
- Smooth 60 FPS maintained during voice interaction

## Troubleshooting

### Microphone Not Working
1. Check browser permissions
2. Verify HTTPS connection (required for getUserMedia)
3. Test microphone in system settings
4. Try different browser

### TTS Not Playing
1. Check browser TTS support
2. Verify speaker/volume settings
3. Try toggling TTS off/on
4. Check browser console for errors

### Voice Recognition Errors
1. Ensure TERAG backend is running
2. Check `/voice/query` endpoint availability
3. Verify audio format compatibility
4. Review network connection

## Future Enhancements

### Planned for v1.2
- [ ] ElevenLabs API integration for premium TTS
- [ ] Multiple voice personas
- [ ] Voice emotion detection
- [ ] Conversation history playback
- [ ] Wake word activation
- [ ] Multi-language support

### Planned for v1.3
- [ ] Real-time transcription display
- [ ] Voice command shortcuts
- [ ] Ambient voice mode
- [ ] Voice-controlled 3D navigation
- [ ] Group voice chat support

## Best Practices

### For Users
- Speak clearly and at normal pace
- Use short, focused queries
- Wait for "Ready" state before next query
- Enable TTS for full immersive experience

### For Developers
- Always handle microphone permission errors
- Cleanup audio streams properly
- Test across multiple browsers
- Monitor performance with voice active
- Provide visual feedback for all states

## Configuration

### Environment Variables

```bash
# .env
VITE_TERAG_API_URL=http://localhost:8000
```

### Voice Settings (code)

```typescript
// VoiceRecorder.tsx
const mediaRecorder = new MediaRecorder(stream, {
  mimeType: 'audio/webm',  // Format
});

// VoiceOutput.tsx
utterance.rate = 0.95;      // Speech speed
utterance.pitch = 1.0;      // Voice pitch
utterance.volume = 0.8;     // Output volume
```

## Credits

- **Speech Recognition**: TERAG v5.1 Backend (Whisper API)
- **TTS**: Web Speech API (browser native)
- **Audio Processing**: MediaRecorder API
- **Visual Design**: TERAG Immersive Shell v1.0

---

**Version**: 1.1.0
**Status**: Production Ready
**Last Updated**: 2025-10-10
**License**: MIT
