import { ReactNode } from 'react';

type CardProps = {
  children: ReactNode;
  title?: string;
  subtitle?: string;
  icon?: ReactNode;
  className?: string;
  hoverable?: boolean;
};

export default function Card({
  children,
  title,
  subtitle,
  icon,
  className,
  hoverable = false,
}: CardProps) {
  const resolvedClassName = [
    'rounded-xl border border-gray-200 bg-white p-6 shadow-sm',
    hoverable ? 'transition-all duration-200 hover:shadow-md' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <section className={resolvedClassName}>
      {(icon || title) && (
        <div className="mb-4 flex items-start gap-3">
          {icon && (
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[#f5f7fa] text-[#11486b]">
              {icon}
            </div>
          )}
          <div>
            {title && <h3 className="text-lg font-semibold text-[#11486b]">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-sm text-gray-500">{subtitle}</p>}
          </div>
        </div>
      )}
      {children}
    </section>
  );
}
