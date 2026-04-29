import { ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger';

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  isLoading?: boolean;
};

const baseClasses =
  'inline-flex items-center justify-center gap-2 rounded-md border px-6 py-3 text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#11486b] focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:cursor-not-allowed disabled:opacity-60';

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'border-transparent bg-[#ffa425] text-black hover:bg-[#e6951f]',
  secondary: 'border-[#11486b] bg-white text-[#11486b] hover:bg-gray-50',
  danger: 'border-transparent bg-[#ac2b49] text-white hover:opacity-90',
};

function LoadingDots() {
  return (
    <span className="loading-dots flex items-center gap-1" aria-label="Loading">
      {[0, 1, 2].map((i) => (
        <span key={i} className="inline-block h-1.5 w-1.5 rounded-full bg-current" />
      ))}
    </span>
  );
}

export default function Button({
  variant = 'primary',
  fullWidth = false,
  isLoading = false,
  className,
  children,
  disabled,
  ...props
}: ButtonProps) {
  const resolvedClassName = [
    baseClasses,
    variantClasses[variant],
    fullWidth ? 'w-full' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button className={resolvedClassName} disabled={disabled || isLoading} {...props}>
      {isLoading ? <LoadingDots /> : children}
    </button>
  );
}
