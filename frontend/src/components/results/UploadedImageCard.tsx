import React from 'react';

interface UploadedImageCardProps {
  preview: string;
  name: string;
  width?: number;
  height?: number;
}

const UploadedImageCard: React.FC<UploadedImageCardProps> = ({
  preview,
  name,
  width,
  height,
}) => {
  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <div className="mb-3">
        <img
          src={preview}
          alt={`Preview of ${name}`}
          className="max-w-full h-auto rounded"
        />
      </div>
      <div className="text-sm text-gray-600 space-y-1">
        <p>
          <strong>Filename:</strong> {name}
        </p>
        {width && height && (
          <p>
            <strong>Dimensions:</strong> {width} × {height} px
          </p>
        )}
      </div>
    </div>
  );
};

export default UploadedImageCard;