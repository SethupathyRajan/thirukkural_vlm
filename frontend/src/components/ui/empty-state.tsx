import React from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactElement;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center ${className}`}>
      {icon && <div className="mb-6">{icon}</div>}
      <h2 className="mb-3 text-2xl font-semibold text-foreground">{title}</h2>
      {description && (
        <p className="mb-6 text-muted-foreground max-w-xl">
          {description}
        </p>
      )}
      {action && <div className="flex justify-center">{action}</div>}
    </div>
  );
};

export { EmptyState };
export default EmptyState;