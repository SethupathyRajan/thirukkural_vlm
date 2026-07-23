import React from 'react';
import Button from '@/components/ui/button';

interface UploadActionsProps {
  onUpload: () => void;
  isUploading: boolean;
  error: string | null;
}

const UploadActions: React.FC<UploadActionsProps> = ({
  onUpload,
  isUploading,
  error,
}) => {
  return (
    <div className="flex flex-col items-center gap-4">
      {error && (
        <div className="w-full p-3 bg-red-50 text-red-600 rounded text-center text-sm">
          {error}
        </div>
      )}
      <Button
        variant="primary"
        onClick={onUpload}
        isLoading={isUploading}
        disabled={isUploading}
        className="w-full md:w-48"
      >
        {isUploading ? 'Analyzing...' : 'Analyze Image'}
      </Button>
    </div>
  );
};

export default UploadActions;