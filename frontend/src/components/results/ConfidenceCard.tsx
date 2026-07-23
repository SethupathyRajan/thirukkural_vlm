import React from 'react';

interface ConfidenceMetrics {
  overall: number;
  imageSimilarity: number;
  knowledgeSimilarity: number;
  combinedScore: number;
}

interface ConfidenceCardProps {
  confidence: ConfidenceMetrics;
}

const ConfidenceCard: React.FC<ConfidenceCardProps> = ({
  confidence,
}) => {
  const { overall, imageSimilarity, knowledgeSimilarity, combinedScore } = confidence;

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 mb-4">Confidence Metrics</h3>
      <div className="space-y-4">
        <div>
          <p className="text-sm font-medium text-gray-700 mb-1">Overall Confidence</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`bg-blue-600 h-2.5 rounded-full`}
              style={{ width: `${overall * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {(overall * 100).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-700 mb-1">Image Similarity</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`bg-green-600 h-2.5 rounded-full`}
              style={{ width: `${imageSimilarity * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {(imageSimilarity * 100).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-700 mb-1">Knowledge Similarity</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`bg-purple-600 h-2.5 rounded-full`}
              style={{ width: `${knowledgeSimilarity * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {(knowledgeSimilarity * 100).toFixed(1)}%
          </p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-700 mb-1">Combined Score</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className={`bg-indigo-600 h-2.5 rounded-full`}
              style={{ width: `${combinedScore * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">
            {(combinedScore * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );
};

export default ConfidenceCard;