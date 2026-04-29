'use client';

import type { Application } from '@/services/application.service';
import type { Internship } from '@/services/internship.service';

import Spinner from '@/components/ui/Spinner';
import InternshipCard from './InternshipCard';

type InternshipListProps = {
  internships: Internship[];
  isLoading?: boolean;
  error?: string | null;
  onApply?: (id: number) => void;
  applyingId?: number | null;
  appliedIds?: Set<number>;
  applicationsByInternshipId?: Map<number, Application>;
};

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-xl border border-gray-200 bg-white px-6 py-16">
      <Spinner label="Loading internships" />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#f5f7fa] text-sm text-[#11486b]">
        0
      </div>
      <h3 className="mt-4 text-lg font-semibold text-[#11486b]">No Internships Found</h3>
      <p className="mt-2 max-w-sm text-sm text-gray-500">
        No internships match your current filters. Try broadening your search criteria.
      </p>
    </div>
  );
}

export default function InternshipList({
  internships,
  isLoading = false,
  error = null,
  onApply,
  applyingId = null,
  appliedIds = new Set(),
  applicationsByInternshipId = new Map(),
}: InternshipListProps) {
  if (isLoading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-[#ac2b49] bg-white px-6 py-5 text-center">
        <p className="text-sm font-medium text-[#ac2b49]">{error}</p>
        <p className="mt-1 text-xs text-gray-500">Please try again or contact support.</p>
      </div>
    );
  }

  if (internships.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      {internships.map((internship) => {
        const application = applicationsByInternshipId.get(internship.id);
        return (
          <InternshipCard
            key={internship.id}
            internship={internship}
            onApply={onApply}
            isApplying={applyingId === internship.id}
            isApplied={appliedIds.has(internship.id)}
            applicationStatus={application?.status ?? null}
          />
        );
      })}
    </div>
  );
}
