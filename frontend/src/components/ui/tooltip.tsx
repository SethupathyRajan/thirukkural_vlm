import React from 'react';

interface TooltipProps {
  children: React.ReactNode;
  content: string;
  side?: 'top' | 'right' | 'bottom' | 'left';
}

const Tooltip: React.FC<TooltipProps> = ({
  children,
  content,
  side = 'top',
  className,
}) => {
  // Simple tooltip implementation
  // In a real app, you might use a library like @radix-ui/react-tooltip
  const [showTooltip, setShowTooltip] = React.useState(false);

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {React.cloneElement(children as React.ReactElement, {
        className: `${(children as React.ReactElement).props?.className ?? ''}`,
      })}
      {showTooltip && (
        <div
          className={`absolute z-50 mb-2 animate-in fade-in-0 zoom-in-95 ${
            side === 'bottom'
              ? 'top-5 left-1/2 -translate-x-1/2'
              : side === 'right'
              ? '-ml-0 left-5 top-1/2 -translate-y-1/2'
              : side === 'left'
              ? '-mr-0 right-5 top-1/2 -translate-y-1/2'
              : 'bottom-5 left-1/2 -translate-x-1/2'
          }`}
        >
          <div className="whitespace-nowrap rounded-md bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-lg border border-popover/50">
            {content}
          </div>
        </div>
      )}
    </div>
  );
};

export { Tooltip };
export default Tooltip;