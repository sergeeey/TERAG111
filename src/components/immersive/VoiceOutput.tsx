import { useEffect, useRef, useState, useCallback } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

interface VoiceOutputProps {
  text: string;
  enabled: boolean;
  onSpeakingStart?: () => void;
  onSpeakingEnd?: () => void;
}

export function useVoiceOutput() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isEnabled, setIsEnabled] = useState(true);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const speak = useCallback((text: string, onStart?: () => void, onEnd?: () => void, language?: string) => {
    if (!isEnabled || !text || typeof window === 'undefined' || !window.speechSynthesis) {
      return;
    }

    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utteranceRef.current = utterance;

    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 0.8;

    const lang = language || document.documentElement.lang || 'en';
    const voices = window.speechSynthesis.getVoices();

    const preferredVoice = voices.find((voice) => {
      if (lang === 'ru' || lang.startsWith('ru')) {
        return voice.lang.startsWith('ru') &&
               (voice.name.includes('Google') || voice.name.includes('Microsoft') || voice.name.includes('Yandex'));
      }
      return voice.lang.startsWith('en') &&
             (voice.name.includes('Google') || voice.name.includes('Microsoft'));
    });

    if (preferredVoice) {
      utterance.voice = preferredVoice;
      utterance.lang = preferredVoice.lang;
    } else {
      utterance.lang = lang === 'ru' ? 'ru-RU' : 'en-US';
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      onStart?.();
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      onEnd?.();
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      onEnd?.();
    };

    window.speechSynthesis.speak(utterance);
  }, [isEnabled]);

  const stop = useCallback(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  const toggleEnabled = useCallback(() => {
    setIsEnabled((prev) => !prev);
    if (isSpeaking) {
      stop();
    }
  }, [isSpeaking, stop]);

  useEffect(() => {
    return () => {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  return {
    speak,
    stop,
    isSpeaking,
    isEnabled,
    toggleEnabled,
  };
}

export function VoiceOutput({ text, enabled, onSpeakingStart, onSpeakingEnd }: VoiceOutputProps) {
  const { speak, isSpeaking } = useVoiceOutput();

  useEffect(() => {
    if (text && enabled) {
      speak(text, onSpeakingStart, onSpeakingEnd);
    }
  }, [text, enabled, speak, onSpeakingStart, onSpeakingEnd]);

  return null;
}

interface VoiceToggleProps {
  enabled: boolean;
  onToggle: () => void;
  isSpeaking?: boolean;
}

export function VoiceToggle({ enabled, onToggle, isSpeaking }: VoiceToggleProps) {
  return (
    <button
      onClick={onToggle}
      className="p-3 rounded-full bg-[#00FFE0]/10 hover:bg-[#00FFE0]/20 transition-all duration-300 relative"
      title={enabled ? 'Disable voice output' : 'Enable voice output'}
    >
      {enabled ? (
        <Volume2 className={`w-5 h-5 text-white ${isSpeaking ? 'animate-pulse' : ''}`} />
      ) : (
        <VolumeX className="w-5 h-5 text-white/50" />
      )}
      {isSpeaking && (
        <span className="absolute -top-1 -right-1 w-3 h-3 bg-[#00FFE0] rounded-full animate-pulse" />
      )}
    </button>
  );
}
