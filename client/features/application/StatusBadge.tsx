import type { ApplicationStatus } from '@/services/application.service';

type StatusBadgeProps = {
  status: ApplicationStatus;
};

const statusConfig: Record<
  ApplicationStatus,
  { label: string; classes: string; dotClass: string }
> = {
  APPLIED: {
    label: 'Applied',
    classes: 'bg-[#f5f7fa] text-gray-600 border-gray-200',
    dotClass: 'bg-gray-500',
  },
  UNDER_REVIEW: {
    label: 'Under Review',
    classes: 'bg-[#ffa425] text-black border-[#ffa425]',
    dotClass: 'bg-black animate-pulse',
  },
  SHORTLISTED: {
    label: 'Shortlisted',
    classes: 'bg-[#da6328] text-white border-[#da6328]',
    dotClass: 'bg-white',
  },
  SELECTED: {
    label: 'Selected',
    classes: 'bg-[#478356] text-white border-[#478356]',
    dotClass: 'bg-white',
  },
  IN_PROGRESS: {
    label: 'In Progress',
    classes: 'bg-[#ffa425] text-black border-[#ffa425]',
    dotClass: 'bg-black animate-pulse',
  },
  REJECTED: {
    label: 'Rejected',
    classes: 'bg-[#ac2b49] text-white border-[#ac2b49]',
    dotClass: 'bg-white',
  },
  COMPLETED: {
    label: 'Completed',
    classes: 'bg-[#478356] text-white border-[#478356]',
    dotClass: 'bg-white',
  },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status] ?? statusConfig.APPLIED;

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold ${config.classes}`}
    >
      <span className={`inline-block h-1.5 w-1.5 rounded-full ${config.dotClass}`} />
      {config.label}
    </span>
  );
}
