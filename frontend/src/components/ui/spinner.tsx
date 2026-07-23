import React from 'react';

interface SpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: number;
  color?: string;
  className?: string;
}

const Spinner: React.FC<SpinnerProps> = ({
  size = 4,
  color = 'currentColor',
  className,
  ...props
}) => {
  return (
    <div
      className={`animate-spin rounded-full h-${size} w-${size} border-b-2 border-${color} ${className ?? ''}`}
      role="status"
      {...props}
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export { Spinner };
export default Spinner;