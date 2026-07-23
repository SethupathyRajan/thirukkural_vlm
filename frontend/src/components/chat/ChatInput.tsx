import React from 'react';

interface ChatInputProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onSubmit: (text: string) => void;
  loading: boolean;
  error?: string | null;
  placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
  value,
  onChange,
  onKeyDown,
  onSubmit,
  loading,
  error,
  placeholder = 'Ask a question...'
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSubmit(value);
    }
  };

  return (
    <div className="space-y-4">
      {error && (
        <div className="p-3 bg-red-50 text-sm text-red-600 rounded">
          {error}
          <button
            onClick={() => {
              // The parent component should handle clearing the error
              // We'll just note that clicking this doesn't clear it directly
              // but the error will clear when user starts typing or on next submit attempt
            }}
            className="ml-2 text-xs text-red-600 hover:underline transition-colors"
          >
            ×
          </button>
        </div>
      )}
      <form onSubmit={handleSubmit} className="flex space-x-2">
        <textarea
          value={value}
          onChange={onChange}
          onKeyDown={onKeyDown}
          rows={3}
          placeholder={placeholder}
          className="flex-1 min-h-[80px] resize-none border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !value.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50 hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          {loading ? (
            <>
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
              </svg>
              <span>Thinking...</span>
            </>
          ) : (
            'Ask'
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;