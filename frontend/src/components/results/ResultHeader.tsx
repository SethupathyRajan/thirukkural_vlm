import React from 'react';
import { useLocation } from 'react-router-dom';

// ResultHeader: Simple header for the results page
const ResultHeader: React.FC = () => {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Analysis Results
      </h1>
    </div>
  );
};

export default ResultHeader;