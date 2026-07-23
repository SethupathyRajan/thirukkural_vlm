import React from 'react';

const UploadPlaceholder: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center p-8 border-2 border-dashed border-gray-300 rounded-lg bg-gray-50">
      <div className="flex items-center space-x-2 mb-4 text-gray-500">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
        </svg>
        <span>Choose an image</span>
      </div>
      <div className="flex items-center space-x-2 mb-2 text-sm text-gray-500">
        <span>or drag and drop</span>
      </div>
      <div className="text-xs text-gray-400">
        PNG, JPG or JPEG
      </div>
    </div>
  );
};

export default UploadPlaceholder;