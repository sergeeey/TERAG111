import { useState, useRef, useEffect } from 'react';
import { Mic, Send, Volume2, VolumeX } from 'lucide-react';

interface CognitiveConsoleProps {
  onQuery: (query: string) => void;
  onVoiceQuery?: (audioBlob: Blob) => void;
  isProcessing: boolean;
  response: string;
}

export function CognitiveConsole({
  onQuery,
  onVoiceQuery,
  isProcessing,
  response,
}: CognitiveConsoleProps) {
  const [query, setQuery] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSoundEnabled, setIsSoundEnabled] = useState(true);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!isProcessing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isProcessing]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isProcessing) {
      onQuery(query.trim());
      setQuery('');
    }
  };

  const startRecording = async () => {
    if (!onVoiceQuery) return;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        onVoiceQuery(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 p-6">
      <div className="max-w-4xl mx-auto">
        {response && (
          <div className="mb-4 p-4 rounded-lg bg-gradient-to-r from-[#00FFE0]/10 to-[#0099FF]/10 border border-[#00FFE0]/30 backdrop-blur-md">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 rounded-full bg-[#00FFE0] mt-2 animate-pulse" />
              <div className="flex-1">
                <p className="text-sm text-[#00FFE0] font-semibold mb-1">TERAG Response</p>
                <p className="text-white/90 leading-relaxed">{response}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="relative">
          <div className="relative bg-gradient-to-r from-[#10131A]/90 to-[#1A1E2E]/90 backdrop-blur-xl rounded-2xl border border-[#00FFE0]/20 shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-[#00FFE0]/5 to-[#FF00FF]/5 pointer-events-none" />

            <div className="relative p-6">
              <div className="flex items-center gap-4">
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask TERAG anything..."
                  disabled={isProcessing || isRecording}
                  className="flex-1 bg-transparent text-white placeholder-white/40 text-lg outline-none"
                />

                <div className="flex items-center gap-2">
                  {onVoiceQuery && (
                    <button
                      type="button"
                      onClick={isRecording ? stopRecording : startRecording}
                      disabled={isProcessing}
                      className={`p-3 rounded-full transition-all duration-300 ${
                        isRecording
                          ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                          : 'bg-[#00FFE0]/10 hover:bg-[#00FFE0]/20'
                      } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      <Mic className="w-5 h-5 text-white" />
                    </button>
                  )}

                  <button
                    type="button"
                    onClick={() => setIsSoundEnabled(!isSoundEnabled)}
                    className="p-3 rounded-full bg-[#00FFE0]/10 hover:bg-[#00FFE0]/20 transition-all duration-300"
                  >
                    {isSoundEnabled ? (
                      <Volume2 className="w-5 h-5 text-white" />
                    ) : (
                      <VolumeX className="w-5 h-5 text-white" />
                    )}
                  </button>

                  <button
                    type="submit"
                    disabled={!query.trim() || isProcessing || isRecording}
                    className="p-3 rounded-full bg-gradient-to-r from-[#00FFE0] to-[#0099FF] hover:from-[#00FFE0]/90 hover:to-[#0099FF]/90 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-[#00FFE0]/20"
                  >
                    <Send className="w-5 h-5 text-[#0A0E1A]" />
                  </button>
                </div>
              </div>

              {isProcessing && (
                <div className="mt-4 flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                    <span className="w-2 h-2 bg-[#00FFE0] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  </div>
                  <span className="text-sm text-[#00FFE0]/70">TERAG is reasoning...</span>
                </div>
              )}

              {isRecording && (
                <div className="mt-4 flex items-center gap-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-sm text-red-400">Recording audio...</span>
                </div>
              )}
            </div>
          </div>

          <div className="mt-3 flex items-center justify-between px-2">
            <p className="text-xs text-white/40">
              Press Enter to send • Use microphone for voice input
            </p>
            <p className="text-xs text-white/40">
              Powered by TERAG v5.1
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
