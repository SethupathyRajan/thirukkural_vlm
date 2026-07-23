import React, { useState } from 'react';
import api from '@/services/api';
import ChatInput from './ChatInput';
import ChatMessage from './ChatMessage';
import ChatHistory from './ChatHistory';
import SuggestedQuestions from './SuggestedQuestions';
import EmptyConversation from './EmptyConversation';

interface ImageData {
  preview: string;
  name: string;
  width?: number;
  height?: number;
}

interface Prediction {
  tirukkuralNumber: number | string;
  tamilCouplet: string;
  englishTranslation: string;
  concept: string;
  confidence: {
    overall: number;
    imageSimilarity: number;
    knowledgeSimilarity: number;
    combinedScore: number;
  };
  explanation?: string;
  alternativeMatches: Array<{
    tirukkuralNumber: number | string;
    tamilCouplet: string;
    englishTranslation: string;
    concept: string;
    combinedScore: number;
  }>;
  analysisSteps: {
    imageAnalyzed: boolean;
    kuralFound: boolean;
    conceptIdentified: boolean;
    explanationGenerated: boolean;
  };
}

interface ChatMessageData {
  role: 'user' | 'assistant';
  content: string;
}

const EducationalChat: React.FC<{
  image: ImageData;
  prediction: Prediction;
}> = ({ image, prediction }) => {
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    setInputValue('');
    setLoading(true);
    setError(null);

    try {
      // Prepare the request body
      // We'll send the message and the prediction context as JSON
      const response = await api.post('/chat', {
        message: text,
        context: prediction
      });

      // Handle different possible response formats
      let botResponse = '';
      if (response.data.response) {
        botResponse = response.data.response;
      } else if (response.data.message) {
        botResponse = response.data.message;
      } else if (typeof response.data === 'string') {
        botResponse = response.data;
      } else {
        // Fallback: try to extract meaningful text
        botResponse = JSON.stringify(response.data);
      }

      setMessages(prev => [...prev, { role: 'assistant', content: botResponse }]);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError('Unable to get a response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim()) {
        sendMessage(inputValue);
      }
    }
    // Allow Shift+Enter for newline
  };

  return (
    <div className="space-y-6">
      {messages.length === 0 ? (
        <>
          <SuggestedQuestions
            questions={[
              'Explain this Kural in simple English.',
              'Give another real-life example.',
              'Why is this important?',
              'How can I apply this in daily life?',
              'Teach this to a school student.',
              'Summarize this Kural.'
            ]}
            onSelect={sendMessage}
          />
          <EmptyConversation message="Start the conversation by asking a question about this Thirukkural." />
        </>
      ) : (
        <ChatHistory messages={messages} />
      )}
      <ChatInput
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        onSubmit={sendMessage}
        loading={loading}
        error={error}
        placeholder="Ask a question about this Thirukkural..."
      />
    </div>
  );
};

export default EducationalChat;