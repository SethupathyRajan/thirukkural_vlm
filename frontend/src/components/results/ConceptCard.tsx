import React from 'react';

interface ConceptCardProps {
  concept: string;
}

const ConceptCard: React.FC<ConceptCardProps> = ({ concept }) => {
  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 mb-2">Ethical Concept Identified</h3>
      <p className="text-gray-700">{concept}</p>
    </div>
  );
};

export default ConceptCard;