import React from 'react';

interface ImagePreviewProps {
  previewUrl: string;
  onRemove: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({
  previewUrl,
  onRemove,
}) => {
  return (
    <div className="relative">
      <img
        src={previewUrl}
        alt="Preview"
        className="max-w-full h-auto rounded-lg"
      />
      <button
        onClick={onRemove}
        className="absolute top-2 right-2 rounded-full bg-white bg-opacity-50 hover:bg-opacity-75 p-1 hover:text-gray-900 transition-colors"
        aria-label="Remove image"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

export default ImagePreview;