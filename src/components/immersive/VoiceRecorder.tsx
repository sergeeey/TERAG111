import { useState, useRef, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';

interface VoiceRecorderProps {
  onRecordingComplete: (audioBlob: Blob) => void;
  isProcessing: boolean;
}

export type VoiceState = 'idle' | 'listening' | 'processing';

export function VoiceRecorder({ onRecordingComplete, isProcessing }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const playSound = useCallback((type: 'start' | 'end') => {
    try {
      const audio = new Audio(type === 'start' ? '/sounds/record_start.wav' : '/sounds/record_end.wav');
      audio.volume = 0.3;
      audio.play().catch(() => {});
    } catch (error) {
      console.log('Sound playback not available');
    }
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      });

      streamRef.current = stream;
      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
      });

      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        onRecordingComplete(audioBlob);

        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }

        playSound('end');
        setVoiceState('processing');
      };

      mediaRecorder.start();
      setIsRecording(true);
      setVoiceState('listening');
      playSound('start');
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Microphone access denied. Please enable microphone permissions.');
    }
  }, [onRecordingComplete, playSound]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return {
    isRecording,
    voiceState: isProcessing ? 'processing' : voiceState,
    toggleRecording,
    stopRecording,
  };
}

interface VoiceButtonProps {
  isRecording: boolean;
  voiceState: VoiceState;
  onToggle: () => void;
  disabled?: boolean;
}

export function VoiceButton({ isRecording, voiceState, onToggle, disabled }: VoiceButtonProps) {
  const getButtonStyle = () => {
    if (voiceState === 'listening') {
      return 'bg-blue-500 hover:bg-blue-600 shadow-lg shadow-blue-500/50 animate-pulse';
    }
    if (voiceState === 'processing') {
      return 'bg-yellow-500 hover:bg-yellow-600 shadow-lg shadow-yellow-500/50';
    }
    return 'bg-[#00FFE0]/10 hover:bg-[#00FFE0]/20';
  };

  const getStateLabel = () => {
    switch (voiceState) {
      case 'listening':
        return 'Listening...';
      case 'processing':
        return 'Thinking...';
      default:
        return 'Voice Mode';
    }
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <button
        onClick={onToggle}
        disabled={disabled}
        className={`p-4 rounded-full transition-all duration-300 ${getButtonStyle()} disabled:opacity-50 disabled:cursor-not-allowed`}
        title={getStateLabel()}
      >
        {isRecording ? (
          <MicOff className="w-6 h-6 text-white" />
        ) : (
          <Mic className="w-6 h-6 text-white" />
        )}
      </button>

      {voiceState !== 'idle' && (
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              voiceState === 'listening'
                ? 'bg-blue-500'
                : voiceState === 'processing'
                ? 'bg-yellow-500'
                : 'bg-[#00FFE0]'
            } animate-pulse`}
          />
          <span className="text-xs text-white/70">{getStateLabel()}</span>
        </div>
      )}
    </div>
  );
}
