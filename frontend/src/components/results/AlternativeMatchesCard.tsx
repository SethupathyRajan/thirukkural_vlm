import React from 'react';

interface AlternativeMatch {
  scenarioId: number | string;
  concept: string;
  combinedScore: number;
}

interface AlternativeMatchesCardProps {
  alternatives: AlternativeMatch[];
}

const AlternativeMatchesCard: React.FC<AlternativeMatchesCardProps> = ({ alternatives }) => {
  if (!alternatives || alternatives.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
        <p className="text-gray-500">No alternative matches found.</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 mb-4">Alternative Matches</h3>
      <div className="space-y-4">
        {alternatives.map((alt, index) => (
          <div key={index} className="border-b pb-4 last:border-b-0 last:pb-0">
            <div className="flex justify-between">
              <div>
                <p className="font-medium text-gray-800">Scenario {alt.scenarioId}</p>
                <p className="text-sm text-gray-600">Concept: {alt.concept}</p>
              </div>
              <div className="text-right">
                <p className="font-medium text-gray-800">
                  {(alt.combinedScore * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-gray-500">Match Score</p>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mt-1">
              <div
                className={`bg-blue-500 h-2.5 rounded-full`}
                style={{ width: `${alt.combinedScore * 100}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlternativeMatchesCard;