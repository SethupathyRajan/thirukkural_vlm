import React from 'react';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'destructive' | 'success' | 'warning';
  className?: string;
}

const variants: Record<string, string> = {
  default: 'bg-background text-primary',
  destructive: 'bg-destructive/50 text-destructive',
  success: 'bg-green-500/50 text-green-600',
  warning: 'bg-yellow-500/50 text-yellow-600',
};

const Alert: React.FC<AlertProps> = ({
  variant = 'default',
  className,
  children,
  ...props
}) => {
  return (
    <div
      role="alert"
      className={`rounded-border p-4 ${variants[variant]} ${className ?? ''}`}
      {...props}
    >
      {children}
    </div>
  );
};

export { Alert };
export default Alert;