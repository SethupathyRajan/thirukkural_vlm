import React from 'react';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
}

const badges = {
  default: 'bg-primary text-primary-foreground',
  secondary: 'bg-secondary text-secondary-foreground',
  destructive: 'bg-destructive text-destructive-foreground',
  outline: 'border border-input bg-background',
};

const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  className,
  ...props
}) => {
  return (
    <div
      className={'inline-flex items-center justify-center rounded-border px-2.5 py-0.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 ' +
        badges[variant] +
        ' ' +
        (className ?? '')}
      {...props}
    >
      {/* Content */}
    </div>
  );
};

export { Badge };
export default Badge;