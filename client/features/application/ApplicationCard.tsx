import type { Application } from '@/services/application.service';
import type { Certificate } from '@/services/certificate.service';
import Button from '@/components/ui/Button';

import StatusBadge from './StatusBadge';

type ApplicationCardProps = {
  application: Application;
  certificate?: Certificate;
  onDownloadCertificate?: (url: string) => void;
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

export default function ApplicationCard({ 
  application, 
  certificate, 
  onDownloadCertificate 
}: ApplicationCardProps) {
  const title = application.internship_title ?? `Internship #${application.internship_id}`;
  const company = application.company_name ?? 'Company details pending';

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0 flex-1">
          <h3 className="text-lg font-bold text-[#11486b]">{title}</h3>
          <p className="mt-1 text-sm text-gray-500 font-medium">{company}</p>
          <div className="mt-3 flex items-center gap-4">
            <span className="text-[11px] text-gray-400 font-medium uppercase tracking-wider">
              Applied {formatDate(application.applied_at)}
            </span>
          </div>
        </div>

        <div className="flex shrink-0 flex-col items-start gap-3 sm:items-end">
          <StatusBadge status={application.status} />
          
          {application.status === 'COMPLETED' && certificate && (
            <Button
              variant="secondary"
              className="mt-1 text-xs h-9 px-4 bg-gradient-to-r from-[#ffa425] to-[#da6328] text-white border-none shadow-sm hover:opacity-90 font-bold flex items-center gap-2"
              onClick={() => onDownloadCertificate?.(certificate.certificate_url)}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Get Certificate
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
