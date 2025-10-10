# Testing TERAG Voice Mode v1.1

## Quick Start Testing Guide

### Prerequisites
- TERAG backend running at `http://localhost:8000`
- Modern browser (Chrome 90+, Firefox 88+, Edge 90+)
- Microphone access
- HTTPS connection (for getUserMedia API)

### Test Steps

#### 1. Start the Application
```bash
npm run dev
```
Navigate to: `http://localhost:5173/immersive`

#### 2. Initial Load Test
- [ ] Welcome screen appears with animated text
- [ ] "Begin Dialogue" button is visible
- [ ] Click button transitions to main interface
- [ ] 3D NeuroSpace loads without errors
- [ ] TERAG core sphere is visible and rotating
- [ ] Metrics HUD shows IEI, Coherence, Faithfulness

#### 3. Text Mode Test
- [ ] Cognitive Console is in Text Mode by default
- [ ] Text input field is focused
- [ ] Type a query: "What is cognitive alignment?"
- [ ] Send button works
- [ ] Core pulses during reasoning
- [ ] Response appears in console
- [ ] Metrics update
- [ ] TTS speaks response (if enabled)

#### 4. Voice Mode Activation
- [ ] Click "Voice Mode" button
- [ ] Interface switches to Voice Mode
- [ ] Microphone button appears
- [ ] Instructions show "Click microphone to start"
- [ ] Browser prompts for microphone permission
- [ ] Grant permission

#### 5. Voice Recording Test
- [ ] Click microphone button
- [ ] Button turns blue and pulses
- [ ] "Listening" indicator appears
- [ ] Status shows "Listening to your voice..."
- [ ] TERAG core turns blue (#4A9EFF)
- [ ] Agent nodes turn blue
- [ ] Speak: "Explain reasoning coherence"
- [ ] Click microphone again to stop
- [ ] "Processing" indicator appears

#### 6. Voice Processing Test
- [ ] Core turns gold (#FFD700)
- [ ] Status shows "TERAG is reasoning..."
- [ ] Audio is uploaded to backend
- [ ] Response appears in console
- [ ] Transcribed text displayed (if available)
- [ ] Metrics update

#### 7. TTS Output Test
- [ ] Response is spoken automatically
- [ ] "Speaking..." indicator appears
- [ ] Speaker icon shows animation
- [ ] Core pulses during speech
- [ ] Speech completes smoothly
- [ ] State returns to "Ready"

#### 8. TTS Toggle Test
- [ ] Click speaker icon to disable
- [ ] Icon changes to muted state
- [ ] Submit another query
- [ ] Response appears but not spoken
- [ ] Click speaker icon to re-enable
- [ ] Next response is spoken

#### 9. Mode Switching Test
- [ ] While in Voice Mode, click "Text Mode"
- [ ] Interface switches to text input
- [ ] Type and send a query
- [ ] Switch back to Voice Mode
- [ ] Record a voice query
- [ ] Both modes work correctly

#### 10. Error Handling Test
- [ ] Deny microphone permission
- [ ] Voice Mode button should handle gracefully
- [ ] Test with TERAG backend offline
- [ ] Should fall back to simulation mode
- [ ] Error messages are clear

#### 11. Visual States Test
| Action | Expected Core Color | Expected State |
|--------|-------------------|---------------|
| Idle | Cyan #00FFE0 | "Ready" |
| Recording | Blue #4A9EFF | "Listening" |
| Processing | Gold #FFD700 | "Thinking" |
| Speaking | White glow | Status indicator |
| High IEI | Bright Cyan | Smooth animation |
| Low IEI | Red #FF6B6B | Warning state |

#### 12. Reasoning Graph Test
- [ ] Click "View Reasoning" button
- [ ] Graph opens in overlay
- [ ] Shows all agent nodes
- [ ] Connections are visible
- [ ] Voice state propagates to graph
- [ ] Record voice in graph view
- [ ] Graph responds to voice states
- [ ] Close button works

#### 13. Performance Test
- [ ] Monitor FPS in dev tools
- [ ] Should maintain 60 FPS
- [ ] Voice recording doesn't lag
- [ ] TTS playback is smooth
- [ ] 3D scene animations fluid
- [ ] No memory leaks after 5 minutes

#### 14. Mobile/Responsive Test (if applicable)
- [ ] Test on tablet view
- [ ] Voice Mode adapts to screen
- [ ] Touch controls work
- [ ] Microphone access on mobile
- [ ] TTS works on mobile browsers

## Expected Behavior Summary

### Voice Flow
```
IDLE (Ready)
  ↓
LISTENING (User speaks, blue core)
  ↓
PROCESSING (TERAG thinks, gold core)
  ↓
SPEAKING (TTS plays, white glow)
  ↓
IDLE (Ready)
```

### Color States
- **Cyan (#00FFE0)**: Ready, normal IEI
- **Blue (#4A9EFF)**: Listening to voice
- **Gold (#FFD700)**: Processing/reasoning
- **Red (#FF6B6B)**: Low IEI warning
- **Magenta (#FF00FF)**: Meta-controller agent

## Common Issues & Solutions

### Issue: Microphone Not Working
**Solution**:
- Check browser permissions
- Ensure HTTPS connection
- Test mic in system settings
- Try different browser

### Issue: TTS Not Playing
**Solution**:
- Verify browser TTS support
- Check speaker/volume settings
- Try toggling TTS off/on
- Check browser console for errors

### Issue: Core Not Changing Colors
**Solution**:
- Check voice state in console
- Verify WebGL is working
- Refresh browser
- Check for JavaScript errors

### Issue: Backend Connection Failed
**Solution**:
- Verify TERAG backend is running
- Check `http://localhost:8000/healthz`
- Review network tab in dev tools
- Check CORS settings

## Browser-Specific Notes

### Chrome
- Best performance
- Full TTS support
- Microphone API works well

### Firefox
- Good performance
- TTS support varies by OS
- May need to enable permissions

### Safari
- TTS support from 14.1+
- May need to enable Web Speech API
- MediaRecorder support limited

### Edge
- Similar to Chrome
- Full feature support
- Good performance

## Debugging Tips

### Enable Verbose Logging
```javascript
// In browser console
localStorage.setItem('debug', 'terag:*');
```

### Check Voice State
```javascript
// In browser console
// Watch voice state changes
window.addEventListener('voiceStateChange', (e) => {
  console.log('Voice State:', e.detail);
});
```

### Monitor API Calls
1. Open browser dev tools
2. Go to Network tab
3. Filter by "voice" or "reasoning"
4. Check request/response

### Check 3D Performance
1. Open dev tools
2. Go to Performance tab
3. Record session
4. Check FPS and frame timing

## Success Criteria

- [ ] All 14 test steps pass
- [ ] No console errors
- [ ] Smooth 60 FPS
- [ ] Voice recording works
- [ ] TTS playback works
- [ ] Visual states correct
- [ ] Mode switching works
- [ ] Error handling graceful
- [ ] Mobile-friendly (bonus)

## Report Template

```
Date: ________
Tester: ________
Browser: ________
OS: ________

Tests Passed: __ / 14
Issues Found: ________
Performance: ________ FPS
Notes: ________
```

---

**Version**: 1.1.0
**Last Updated**: 2025-10-10
