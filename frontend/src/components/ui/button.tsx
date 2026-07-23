import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  block?: boolean;
  isLoading?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  block = false,
  isLoading = false,
  className,
  children,
  ...props
}) => {
  const baseClasses = 'flex items-center justify-center gap-2 font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';

  const variantClasses = {
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 focus:ring-primary/20',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80 focus:ring-secondary/20',
    outline: 'border border-input hover:bg-accent hover:text-accent-foreground focus:ring-accent/20',
    ghost: 'hover:bg-accent hover:text-accent-foreground focus:ring-accent/20',
  };

  const sizeClasses = {
    sm: 'h-9 px-3 text-sm',
    md: 'h-10 px-4 py-2 text-sm',
    lg: 'h-11 px-8 text-md',
  };

  const blockClass = block ? 'w-full' : '';

  // If loading, show spinner and disable button
  if (isLoading) {
    return (
      <button
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${blockClass} ${className ?? ''}`}
        disabled
        {...props}
      >
        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
        </svg>
        <span className="sr-only">Loading...</span>
      </button>
    );
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${blockClass} ${className ?? ''}`}
      {...props}
    >
      {children}
    </button>
  );
};

export { Button };
export default Button;