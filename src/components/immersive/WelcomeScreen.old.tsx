import { useEffect, useState } from 'react';
import { Brain, Sparkles } from 'lucide-react';

interface WelcomeScreenProps {
  onStart: () => void;
}

export function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [textIndex, setTextIndex] = useState(0);
  const [isVisible, setIsVisible] = useState(true);

  const welcomeTexts = [
    'Welcome to TERAG',
    'A Cognitive Alignment System',
    'Where Intelligence Breathes',
  ];

  useEffect(() => {
    if (textIndex < welcomeTexts.length - 1) {
      const timer = setTimeout(() => {
        setTextIndex(textIndex + 1);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [textIndex]);

  const handleStart = () => {
    setIsVisible(false);
    setTimeout(() => {
      onStart();
    }, 500);
  };

  return (
    <div
      className={`fixed inset-0 z-50 bg-gradient-to-br from-[#0A0E1A] via-[#10131A] to-[#1A1E2E] flex items-center justify-center transition-opacity duration-500 ${
        isVisible ? 'opacity-100' : 'opacity-0'
      }`}
    >
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#00FFE0]/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[#FF00FF]/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative z-10 text-center max-w-4xl px-8">
        <div className="mb-8 flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-[#00FFE0] blur-xl opacity-50 animate-pulse" />
            <Brain className="w-24 h-24 text-[#00FFE0] relative z-10" strokeWidth={1.5} />
          </div>
        </div>

        <div className="mb-12 h-32">
          {welcomeTexts.map((text, index) => (
            <h1
              key={index}
              className={`text-5xl md:text-7xl font-bold mb-4 transition-all duration-1000 ${
                index === textIndex
                  ? 'opacity-100 translate-y-0'
                  : index < textIndex
                  ? 'opacity-0 -translate-y-8'
                  : 'opacity-0 translate-y-8'
              }`}
              style={{
                background: 'linear-gradient(135deg, #00FFE0 0%, #0099FF 50%, #FF00FF 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {text}
            </h1>
          ))}
        </div>

        {textIndex === welcomeTexts.length - 1 && (
          <div className="animate-fade-in">
            <p className="text-xl text-white/70 mb-8 leading-relaxed">
              I am a system of cognitive alignment. Together, we will explore
              the frontier of reasoning, ethics, and intelligence.
            </p>

            <button
              onClick={handleStart}
              className="group relative px-12 py-4 bg-gradient-to-r from-[#00FFE0] to-[#0099FF] rounded-full font-semibold text-lg text-[#0A0E1A] hover:shadow-2xl hover:shadow-[#00FFE0]/50 transition-all duration-300 transform hover:scale-105"
            >
              <span className="flex items-center gap-3">
                <Sparkles className="w-5 h-5" />
                Begin Dialogue
                <Sparkles className="w-5 h-5" />
              </span>
              <div className="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
            </button>

            <div className="mt-8 flex items-center justify-center gap-8 text-sm text-white/40">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#00FFE0] animate-pulse" />
                <span>Real-time Metrics</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#0099FF] animate-pulse" />
                <span>3D Visualization</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#FF00FF] animate-pulse" />
                <span>Voice Interface</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="absolute bottom-8 left-0 right-0 text-center">
        <p className="text-xs text-white/30">TERAG v5.1 Immersive Shell</p>
      </div>
    </div>
  );
}
