'use client';

import { ReactNode, useEffect, useRef } from 'react';
import Button from './Button';

type ModalProps = {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  variant?: 'default' | 'danger';
};

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  footer,
  variant = 'default',
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" 
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div 
        ref={modalRef}
        className="relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white shadow-2xl transition-all"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
          <h3 
            id="modal-title" 
            className={`text-lg font-semibold ${variant === 'danger' ? 'text-red-600' : 'text-gray-900'}`}
          >
            {title}
          </h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
          >
            <span className="sr-only">Close</span>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-6 text-sm text-gray-600">
          {children}
        </div>

        <div className="px-6 py-4 bg-gray-50 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          {footer ? (
            footer
          ) : (
            <>
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
              <Button 
                variant={variant === 'danger' ? 'primary' : 'primary'} 
                onClick={onClose}
                className={variant === 'danger' ? 'bg-red-600 hover:bg-red-700 border-red-600' : ''}
              >
                Confirm
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
