import { ReactNode } from 'react';

type PageHeaderProps = {
  title: string;
  description?: string;
  meta?: ReactNode;
  actions?: ReactNode;
  align?: 'left' | 'center';
  className?: string;
};

export default function PageHeader({
  title,
  description,
  meta,
  actions,
  align = 'left',
  className,
}: PageHeaderProps) {
  const isCentered = align === 'center';
  const containerClasses = isCentered
    ? 'flex flex-col items-center gap-3 text-center'
    : 'flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between';
  const actionsClasses = isCentered
    ? 'flex items-center justify-center gap-2'
    : 'flex items-center gap-2';

  return (
    <div className={[containerClasses, className].filter(Boolean).join(' ')}>
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold text-[#11486b]">{title}</h1>
        {meta && <div className="text-sm text-gray-500">{meta}</div>}
        {description && <p className="text-sm text-gray-500">{description}</p>}
      </div>
      {actions && <div className={actionsClasses}>{actions}</div>}
    </div>
  );
}
