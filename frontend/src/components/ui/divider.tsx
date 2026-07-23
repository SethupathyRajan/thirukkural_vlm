import React from 'react';

interface DividerProps extends React.HTMLAttributes<HTMLHRElement> {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
}

const Divider: React.FC<DividerProps> = ({
  orientation = 'horizontal',
  className,
  ...props
}) => {
  const baseClasses = 'flex items-center justify-center';
  const orientationClasses = {
    horizontal: 'w-full h-px',
    vertical: 'h-full w-px',
  };

  return (
    <hr
      className={`${baseClasses} ${orientationClasses[orientation]} bg-muted ${className ?? ''}`}
      role="separator"
      {...props}
    />
  );
};

export { Divider };
export default Divider;