import Button from '@/components/ui/Button';
import StatusBadge from '@/features/application/StatusBadge';
import type { ApplicationStatus } from '@/services/application.service';
import type { Internship } from '@/services/internship.service';

type InternshipCardProps = {
  internship: Internship;
  onApply?: (id: number) => void;
  isApplying?: boolean;
  isApplied?: boolean;
  applicationStatus?: ApplicationStatus | null;
};

export default function InternshipCard({
  internship,
  onApply,
  isApplying = false,
  isApplied = false,
  applicationStatus = null,
}: InternshipCardProps) {
  return (
    <div className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-semibold text-[#11486b]">{internship.title}</h3>

          <p className="mt-1 flex items-center gap-1.5 text-sm text-gray-600">
            <svg
              className="h-4 w-4 shrink-0 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21"
              />
            </svg>
            {internship.company_name}
          </p>

          <p className="mt-2 text-sm leading-relaxed text-gray-500 line-clamp-2">
            {internship.description}
          </p>

          <div className="mt-3 flex flex-wrap gap-2">
            <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
              {internship.sector}
            </span>
            <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
              📍 {internship.location}
            </span>
            <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
              ⏱️ {internship.duration} weeks
            </span>
            <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
              ₹{internship.stipend.toLocaleString('en-IN')}
            </span>
          </div>
        </div>

        <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
          {applicationStatus && <StatusBadge status={applicationStatus} />}
          <Button
            variant={isApplied ? 'secondary' : 'primary'}
            className="shrink-0 text-xs sm:self-center"
            onClick={() => onApply?.(internship.id)}
            isLoading={isApplying}
            disabled={isApplied}
          >
            {isApplied ? 'Applied' : 'Apply Now'}
          </Button>
        </div>
      </div>
    </div>
  );
}
