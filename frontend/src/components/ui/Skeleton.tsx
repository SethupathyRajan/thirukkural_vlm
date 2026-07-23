import React from 'react';

const Skeleton: React.FC<{ height?: number; width?: string | number }> = ({
  height = 16,
  width = '100%',
}) => {
  return (
    <div
      className="h-4 w-full bg-gray-200 rounded animate-pulse"
      style={{ height: `${height}px`, width: typeof width === 'string' ? width : `${width}px` }}
    />
  );
};

export default Skeleton;