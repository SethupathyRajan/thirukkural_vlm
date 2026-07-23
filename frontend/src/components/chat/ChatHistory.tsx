import React from 'react';
import ChatMessage from './ChatMessage';

interface ChatHistoryProps {
  messages: {
    role: 'user' | 'assistant';
    content: string;
  }[];
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ messages }) => {
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      {messages.map((msg, index) => (
        <div key={index}>
          <ChatMessage role={msg.role} content={msg.content} />
        </div>
      ))}
    </div>
  );
};

export default ChatHistory;