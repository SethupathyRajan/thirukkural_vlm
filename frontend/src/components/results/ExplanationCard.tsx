import React from 'react';

interface ExplanationCardProps {
  explanation?: string;
}

const ExplanationCard: React.FC<ExplanationCardProps> = ({ explanation }) => {
  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      {explanation && (
        <>
          <h3 className="font-medium text-gray-800 mb-2">Explanation:</h3>
          <p className="text-gray-700">{explanation}</p>
        </>
      )}
    </div>
  );
};

export default ExplanationCard;