import React from 'react';

interface EmptyConversationProps {
  message?: string;
}

const EmptyConversation: React.FC<EmptyConversationProps> = ({ message }) => {
  if (!message) {
    return null;
  }

  return (
    <div className="text-center py-8">
      <p className="text-gray-500">{message}</p>
    </div>
  );
};

export default EmptyConversation;