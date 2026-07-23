import React from 'react';

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onSelect
}) => {
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-500 mb-2">
        Suggested questions:
      </p>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onSelect(question)}
            className="px-3 py-1.5 text-sm font-medium bg-gray-50 rounded-full hover:bg-gray-100 transition-colors border border-gray-200"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SuggestedQuestions;