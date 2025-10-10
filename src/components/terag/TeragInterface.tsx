import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'terag';
  content: string;
  timestamp: Date;
  confidence?: number;
}

export function TeragInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'terag',
      content: 'Привет! Я TERAG - ваша когнитивная операционная система. Чем могу помочь?',
      timestamp: new Date(),
      confidence: 100
    }
  ]);
  
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate TERAG response
    setTimeout(() => {
      const teragResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'terag',
        content: generateTeragResponse(inputValue),
        timestamp: new Date(),
        confidence: Math.floor(Math.random() * 20) + 80
      };
      
      setMessages(prev => [...prev, teragResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const generateTeragResponse = (input: string): string => {
    const responses = [
      'Анализирую ваш запрос... Обнаружены интересные паттерны в данных.',
      'Обрабатываю информацию через нейронную сеть. Результат готов.',
      'Использую граф знаний для поиска релевантной информации.',
      'Применяю когнитивные алгоритмы для генерации ответа.',
      'Интегрирую данные из множественных источников для полного ответа.'
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const toggleListening = () => {
    setIsListening(!isListening);
    // Here you would integrate with Web Speech API
  };

  const toggleSpeaking = () => {
    setIsSpeaking(!isSpeaking);
    // Here you would integrate with Text-to-Speech API
  };

  return (
    <div className="bg-black/20 backdrop-blur-xl border border-terag-accent/20 rounded-xl p-6 h-96 flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold font-display">TERAG Interface</h2>
        <div className="flex items-center space-x-2">
          <motion.button
            onClick={toggleListening}
            className={`p-2 rounded-lg transition-colors ${
              isListening ? 'bg-red-500 text-white' : 'bg-terag-accent/20 text-terag-accent'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </motion.button>
          
          <motion.button
            onClick={toggleSpeaking}
            className={`p-2 rounded-lg transition-colors ${
              isSpeaking ? 'bg-blue-500 text-white' : 'bg-terag-accent/20 text-terag-accent'
            }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isSpeaking ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
          </motion.button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 mb-4">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-terag-accent text-black'
                  : 'bg-black/30 text-terag-text-primary border border-terag-accent/20'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              {message.confidence && (
                <div className="mt-2 flex items-center space-x-2">
                  <div className="text-xs text-terag-text-muted">
                    Уверенность: {message.confidence}%
                  </div>
                  <div className="flex-1 bg-gray-600 rounded-full h-1">
                    <div
                      className="bg-terag-accent h-1 rounded-full"
                      style={{ width: `${message.confidence}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        ))}
        
        {isTyping && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="bg-black/30 border border-terag-accent/20 rounded-lg px-4 py-2">
              <div className="flex space-x-1">
                <motion.div
                  className="w-2 h-2 bg-terag-accent rounded-full"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="w-2 h-2 bg-terag-accent rounded-full"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="w-2 h-2 bg-terag-accent rounded-full"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Введите ваш вопрос..."
          className="flex-1 bg-black/30 border border-terag-accent/20 rounded-lg px-4 py-2 text-terag-text-primary placeholder-terag-text-muted focus:outline-none focus:ring-2 focus:ring-terag-accent/50"
        />
        <motion.button
          onClick={handleSendMessage}
          disabled={!inputValue.trim()}
          className="bg-terag-accent text-black p-2 rounded-lg hover:bg-terag-accent/80 disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Send className="w-4 h-4" />
        </motion.button>
      </div>
    </div>
  );
}