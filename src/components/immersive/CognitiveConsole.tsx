import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { VoiceRecorder, VoiceButton, type VoiceState } from './VoiceRecorder';
import { VoiceToggle, useVoiceOutput } from './VoiceOutput';
import { useLanguage } from '../../i18n/LanguageContext';

interface CognitiveConsoleProps {
  onQuery: (query: string) => void;
  onVoiceQuery?: (audioBlob: Blob) => void;
  isProcessing: boolean;
  response: string;
  voiceState?: VoiceState;
  onVoiceStateChange?: (state: VoiceState) => void;
}

export function CognitiveConsole({
  onQuery,
  onVoiceQuery,
  isProcessing,
  response,
  voiceState: externalVoiceState,
  onVoiceStateChange,
}: CognitiveConsoleProps) {
  const [query, setQuery] = useState('');
  const [isVoiceModeEnabled, setIsVoiceModeEnabled] = useState(false);
  const [transcribedText, setTranscribedText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const { t } = useLanguage();

  const { speak, isSpeaking, isEnabled: isSoundEnabled, toggleEnabled: toggleSound } = useVoiceOutput();

  const voiceRecorder = VoiceRecorder({
    onRecordingComplete: (audioBlob) => {
      if (onVoiceQuery) {
        onVoiceQuery(audioBlob);
      }
    },
    isProcessing,
  });

  const currentVoiceState = externalVoiceState || voiceRecorder.voiceState;

  useEffect(() => {
    if (onVoiceStateChange) {
      onVoiceStateChange(currentVoiceState);
    }
  }, [currentVoiceState, onVoiceStateChange]);

  useEffect(() => {
    if (!isProcessing && inputRef.current && !isVoiceModeEnabled) {
      inputRef.current.focus();
    }
  }, [isProcessing, isVoiceModeEnabled]);

  useEffect(() => {
    if (response && isSoundEnabled && !isProcessing) {
      const handleSpeakingStart = () => {
        if (onVoiceStateChange) {
          onVoiceStateChange('processing');
        }
      };

      const handleSpeakingEnd = () => {
        if (onVoiceStateChange) {
          onVoiceStateChange('idle');
        }
      };

      speak(response, handleSpeakingStart, handleSpeakingEnd);
    }
  }, [response, isSoundEnabled, isProcessing, speak, onVoiceStateChange]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isProcessing) {
      onQuery(query.trim());
      setQuery('');
      setTranscribedText('');
    }
  };

  const handleVoiceModeToggle = () => {
    setIsVoiceModeEnabled(!isVoiceModeEnabled);
    if (voiceRecorder.isRecording) {
      voiceRecorder.stopRecording();
    }
  };

  const getStatusMessage = () => {
    if (currentVoiceState === 'listening') return t('states.listening');
    if (currentVoiceState === 'processing') return t('states.reasoning');
    if (isSpeaking) return t('states.speaking');
    if (isProcessing) return t('states.reasoning');
    return '';
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-6">
      <div className="max-w-4xl mx-auto">
        {response && (
          <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-[#00FFE0]/10 to-[#0099FF]/10 border border-[#00FFE0]/30 backdrop-blur-md animate-fade-in">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-[#00FFE0] mt-2 animate-pulse" />
              <div className="flex-1">
                <p className="text-sm text-[#00FFE0] font-semibold mb-1">{t('console.response')}</p>
                <p className="text-white/90 leading-relaxed">{response}</p>
                {isSpeaking && (
                  <div className="mt-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-[#00FFE0] animate-pulse" />
                    <span className="text-xs text-[#00FFE0]/70">{t('console.speaking')}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {transcribedText && (
          <div className="mb-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30 backdrop-blur-md">
            <p className="text-sm text-blue-300">
              <span className="font-semibold">{t('console.transcribed')}: </span>
              {transcribedText}
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="relative">
          <div className="relative bg-gradient-to-r from-[#10131A]/90 to-[#1A1E2E]/90 backdrop-blur-xl rounded-2xl border border-[#00FFE0]/20 shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#00FFE0]/5 to-[#FF00FF]/5 pointer-events-none" />

            <div className="relative p-6">
              <div className="flex items-center gap-4">
                {!isVoiceModeEnabled ? (
                  <>
                    <input
                      ref={inputRef}
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder={t('console.placeholder')}
                      disabled={isProcessing}
                      className="flex-1 bg-transparent text-white placeholder-white/40 text-lg outline-none"
                    />

                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={handleVoiceModeToggle}
                        className="px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/20 to-[#00FFE0]/20 hover:from-blue-500/30 hover:to-[#00FFE0]/30 transition-all duration-300 border border-blue-500/30 text-sm font-semibold text-white"
                      >
                        {t('console.voiceMode')}
                      </button>

                      <VoiceToggle
                        enabled={isSoundEnabled}
                        onToggle={toggleSound}
                        isSpeaking={isSpeaking}
                      />

                      <button
                        type="submit"
                        disabled={!query.trim() || isProcessing}
                        className="p-3 rounded-full bg-gradient-to-r from-[#00FFE0] to-[#0099FF] hover:from-[#00FFE0]/90 hover:to-[#0099FF]/90 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#00FFE0]/20"
                      >
                        <Send className="w-5 h-5 text-[#0A0E1A]" />
                      </button>
                    </div>
                  </>
                ) : (
                  <div className="flex-1 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <VoiceButton
                        isRecording={voiceRecorder.isRecording}
                        voiceState={currentVoiceState}
                        onToggle={voiceRecorder.toggleRecording}
                        disabled={isProcessing}
                      />

                      <div className="text-left">
                        <p className="text-white font-semibold">{t('console.voiceModeActive')}</p>
                        <p className="text-sm text-white/50">{t('console.clickToStart')}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <VoiceToggle
                        enabled={isSoundEnabled}
                        onToggle={toggleSound}
                        isSpeaking={isSpeaking}
                      />

                      <button
                        type="button"
                        onClick={handleVoiceModeToggle}
                        className="px-4 py-2 rounded-full bg-white/5 hover:bg-white/10 transition-all duration-300 text-sm font-semibold text-white"
                      >
                        {t('console.textMode')}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {getStatusMessage() && (
                <div className="mt-4 flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm text-[#00FFE0]/70">{getStatusMessage()}</span>
                </div>
              )}
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between px-2">
            <p className="text-xs text-white/40">
              {isVoiceModeEnabled
                ? `${t('console.clickToStart')} • ${t('console.textMode')}`
                : `${t('console.pressEnter')} • ${t('console.clickToSpeak')}`}
            </p>
            <p className="text-xs text-white/40">{t('console.poweredBy')}</p>
          </div>
        </form>
      </div>
    </div>
  );
}
