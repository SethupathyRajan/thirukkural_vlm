import React from 'react';

const Loading: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      <p className="mt-2 text-sm text-gray-600">Loading...</p>
    </div>
  );
};

export default Loading;