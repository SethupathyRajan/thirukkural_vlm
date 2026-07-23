import React, { useState } from 'react';
import UploadPlaceholder from './UploadPlaceholder';
import ImagePreview from './ImagePreview';
import UploadActions from './UploadActions';

interface ImageUploaderProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
  error: string | null;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUpload,
  isUploading,
  error,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
    // Reset the input to allow re-selecting the same file
    e.target.value = '';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  };

  const handleFile = (selectedFile: File) => {
    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(selectedFile.type)) {
      setUploadError('Unsupported file type. Please upload a PNG, JPG, or JPEG image.');
      return;
    }

    // Validate file size (e.g., 5MB)
    const maxSizeInBytes = 5 * 1024 * 1024; // 5MB
    if (selectedFile.size > maxSizeInBytes) {
      setUploadError('File size too large. Please upload an image smaller than 5MB.');
      return;
    }

    setFile(selectedFile);
    setUploadError(null);

    // Create preview URL
    const preview = URL.createObjectURL(selectedFile);
    setPreviewUrl(preview);
  };

  const handleRemoveFile = () => {
    setFile(null);
    setPreviewUrl(null);
    setUploadError(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
  };

  const handleUploadClick = async () => {
    if (!file) return;
    setUploadError(null);
    try {
      await onUpload(file);
    } catch (err) {
      // Error is handled in the Home component, but we can set a local error too
      setUploadError('Unable to analyze the image. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors"
      >
        {file ? (
          <ImagePreview
            previewUrl={previewUrl}
            onRemove={handleRemoveFile}
          />
        ) : (
          <UploadPlaceholder>
            <p className="text-sm text-gray-600">
              Choose an image<br />
              <span className="block text-xs text-gray-500">or drag and drop</span>
            </p>
            <p className="mt-2 text-xs text-gray-500">
              PNG, JPG or JPEG
            </p>
          </UploadPlaceholder>
        )}
      </div>

      {file && (
        <UploadActions
          onUpload={handleUploadClick}
          isUploading={isUploading}
          error={uploadError}
        />
      )}
    </div>
  );
};

export default ImageUploader;