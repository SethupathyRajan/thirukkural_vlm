import React from 'react';

// Card component with optional header, title, content, and footer
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ className, children, ...props }) => {
  return (
    <div
      className={'rounded-lg border bg-gray-50 text-gray-900 shadow-sm border-gray-200 ' + (className ?? '')}
      {...props}
    >
      {children}
    </div>
  );
};

// CardHeader
interface CardHeaderProps {
  className?: string;
}

const CardHeader: React.FC<CardHeaderProps> = ({ className, children, ...props }) => {
  return (
    <div className={'flex flex-col space-y-2 pb-6 ' + (className ?? '')} {...props}>
      {children}
    </div>
  );
};

// CardTitle
interface CardTitleProps {
  className?: string;
}

const CardTitle: React.FC<CardTitleProps> = ({ className, children, ...props }) => {
  return (
    <h2 className={'text-xl font-semibold leading-none tracking-tight ' + (className ?? '')} {...props}>
      {children}
    </h2>
  );
};

// CardContent
interface CardContentProps {
  className?: string;
}

const CardContent: React.FC<CardContentProps> = ({ className, children, ...props }) => {
  return (
    <div className={'pt-0 ' + (className ?? '')} {...props}>
      {children}
    </div>
  );
};

// CardFooter
interface CardFooterProps {
  className?: string;
}

const CardFooter: React.FC<CardFooterProps> = ({ className, children, ...props }) => {
  return (
    <div className={'flex items-center space-x-2 pt-6 ' + (className ?? '')} {...props}>
      {children}
    </div>
  );
};

export { Card, CardHeader, CardTitle, CardContent, CardFooter };
export default Card;