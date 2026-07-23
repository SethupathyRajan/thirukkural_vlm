import React from 'react';

interface KuralCardProps {
  tirukkuralNumber: number | string;
  tamilCouplet: string;
  englishTranslation: string;
}

const KuralCard: React.FC<KuralCardProps> = ({
  tirukkuralNumber,
  tamilCouplet,
  englishTranslation,
}) => {
  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <div className="mb-3">
        <h3 className="font-semibold text-gray-800">
          Thirukkural {tirukkuralNumber}
        </h3>
      </div>
      <div className="mb-4 space-y-2">
        <p className="text-lg font-medium text-gray-900">{tamilCouplet}</p>
        <p className="text-gray-600 italic">{englishTranslation}</p>
      </div>
    </div>
  );
};

export default KuralCard;