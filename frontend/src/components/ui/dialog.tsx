import React, { useEffect } from 'react';
import { DialogPortal } from '@radix-ui/react-dialog';
import { DialogOverlay } from '@radix-ui/react-dialog';
import { DialogContent } from '@radix-ui/react-dialog';
import { DialogHeader } from '@radix-ui/react-dialog';
import { DialogTitle } from '@radix-ui/react-dialog';
import { DialogDescription } from '@radix-ui/react-dialog';
import { DialogTrigger } from '@radix-ui/react-dialog';
import { DialogClose } from '@radix-ui/react-dialog';

// Note: This requires @radix-ui/react-dialog to be installed
// For now, we'll create a simple version without the dependency

interface DialogProps extends React.ComponentPropsWithoutRef<'div'> {
  open: boolean;
  onOpenChange: (open: boolean) => boolean;
  children: React.ReactNode;
}

const Dialog: React.FC<DialogProps> = ({ open, onOpenChange, children }) => {
  const handleClose = () => {
    onOpenChange(false);
  };

  useEffect(() => {
    if (!onOpenChange) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onOpenChange(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onOpenChange]);

  if (!open) return null;

  return (
    <>
      <div className="fixed inset-0 z-50 flex items-end justify-center px-4 py-6 sm:mt-0 sm:items-center sm:justify-center">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={handleClose} />
        <div className="relative w-full max-w-md">
          <div className="relative bg-white rounded-lg shadow">
            <div className="p-6">
              <div className="space-y-6">
                <div className="space-y-4">{children}</div>
                <div className="flex justify-end space-x-3">
                  <button
                    onClick={handleClose}
                    className="rounded-md bg-gray-200 px-3 py-2 text-sm font-medium text-gray-900 hover:bg-gray-300 focus:outline-none focus:ring-2 ring-ring"
                  >
                    Cancel
                  </button>
                  <button
                    className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 focus:outline-none focus:ring-2 ring-ring"
                  >
                    Confirm
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export { Dialog };
export default Dialog;