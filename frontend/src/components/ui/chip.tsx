import React from 'react';

interface ChipProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
}

const Chip: React.FC<ChipProps> = ({
  variant = 'default',
  className,
  ...props
}) => {
  const variants: Record<string, string> = {
    default: 'bg-primary text-primary-foreground',
    secondary: 'bg-secondary text-secondary-foreground',
    destructive: 'bg-destructive text-destructive-foreground',
    outline: 'border border-input bg-background',
  };

  return (
    <div
      className={`inline-flex items-center justify-center rounded-touch px-2 pt-0.5 pb-0.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ${
        variants[variant]
      } ${className ?? ''}`}
      {...props}
    >
      {/* Content */}
    </div>
  );
};

export { Chip };
export default Chip;