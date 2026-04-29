import type { Application } from '@/services/application.service';

import StatusBadge from './StatusBadge';

type ApplicationCardProps = {
  application: Application;
};

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return dateString;
  }
}

export default function ApplicationCard({ application }: ApplicationCardProps) {
  const title = application.internship_title ?? `Internship #${application.internship_id}`;
  const company = application.company_name ?? 'Company details pending';

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-base font-semibold text-[#11486b]">{title}</h3>
          <p className="mt-1 text-sm text-gray-500">{company}</p>
        </div>

        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          <StatusBadge status={application.status} />
          <span className="text-xs text-gray-500">
            Applied {formatDate(application.applied_at)}
          </span>
        </div>
      </div>
    </div>
  );
}
