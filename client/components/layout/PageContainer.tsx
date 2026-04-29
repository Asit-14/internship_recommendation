import { ReactNode } from 'react';

type PageContainerProps = {
  children: ReactNode;
  className?: string;
};

export default function PageContainer({ children, className }: PageContainerProps) {
  const resolvedClassName = ['mx-auto w-full max-w-7xl px-4', className].filter(Boolean).join(' ');

  return <div className={resolvedClassName}>{children}</div>;
}
