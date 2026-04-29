type SpinnerProps = {
  label?: string;
  size?: 'sm' | 'md';
};

const sizeClasses: Record<NonNullable<SpinnerProps['size']>, string> = {
  sm: 'h-4 w-4 border-2',
  md: 'h-6 w-6 border-2',
};

export default function Spinner({ label = 'Loading', size = 'md' }: SpinnerProps) {
  return (
    <div className="inline-flex items-center gap-2 text-sm text-gray-500">
      <span
        className={`inline-block animate-spin rounded-full border border-gray-300 border-t-[#11486b] ${sizeClasses[size]}`}
        aria-hidden
      />
      <span>{label}</span>
    </div>
  );
}
