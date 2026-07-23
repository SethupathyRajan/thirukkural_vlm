import React from 'react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  const isUser = role === 'user';

  return (
    <div className="mb-4 max-w-[80%]">
      <div className={`${isUser ? 'ml-auto' : 'mr-auto'}`}>
        <div
          className={`max-w-xs rounded-xl px-4 py-3 text-sm ${
            isUser
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {content}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;