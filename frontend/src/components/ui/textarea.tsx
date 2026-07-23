import React from 'react';

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'outline' | 'filled';
  size?: 'sm' | 'md' | 'lg';
}

const TextArea: React.FC<TextAreaProps> = ({
  variant = 'default',
  size = 'md',
  className,
  ...props
}) => {
  const baseClasses = 'flex min-h-[80px] w-full rounded-md border border-bg bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 resize-none disabled:cursor-not-allowed disabled:opacity-50';

  const variantClasses = {
    default: '',
    outline: 'border-input',
    filled: 'bg-accent/90',
  };

  const sizeClasses = {
    sm: 'h-9 rounded-md px-3 text-sm',
    md: 'h-10 rounded-md px-3 py-2 text-sm',
    lg: 'h-11 rounded-md px-3 py-2 text-sm',
  };

  return (
    <textarea
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className ?? ''}`}
      {...props}
    />
  );
};

export { TextArea };
export default TextArea;