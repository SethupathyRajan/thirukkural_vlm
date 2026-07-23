import React from 'react';

// AnalysisSummaryCard: Displays a checklist of the analysis steps
interface AnalysisSummaryCardProps {
  imageAnalyzed: boolean;
  kuralFound: boolean;
  conceptIdentified: boolean;
  explanationGenerated: boolean;
}

const AnalysisSummaryCard: React.FC<AnalysisSummaryCardProps> = ({
  imageAnalyzed,
  kuralFound,
  conceptIdentified,
  explanationGenerated,
}) => {
  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 p-4">
      <h3 className="font-semibold text-gray-900 mb-3">Analysis Summary</h3>
      <div className="space-y-2">
        <div className="flex items-start">
          <span className="flex-shrink-0">
            {imageAnalyzed ? '✓' : '✗'}
          </span>
          <span className="ml-2">Image analyzed</span>
        </div>
        <div className="flex items-start">
          <span className="flex-shrink-0">
            {kuralFound ? '✓' : '✗'}
          </span>
          <span className="ml-2">Matching Kural found</span>
        </div>
        <div className="flex items-start">
          <span className="flex-shrink-0">
            {conceptIdentified ? '✓' : '✗'}
          </span>
          <span className="ml-2">Ethical concept identified</span>
        </div>
        <div className="flex items-start">
          <span className="flex-shrink-0">
            {explanationGenerated ? '✓' : '✗'}
          </span>
          <span className="ml-2">Explanation generated</span>
        </div>
      </div>
    </div>
  );
};

export default AnalysisSummaryCard;