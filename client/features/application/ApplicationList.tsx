'use client';

import Link from 'next/link';

import Button from '@/components/ui/Button';
import Spinner from '@/components/ui/Spinner';
import type { Application } from '@/services/application.service';

import ApplicationCard from './ApplicationCard';

type ApplicationListProps = {
  applications: Application[];
  isLoading?: boolean;
  error?: string | null;
  onRetry?: () => void;
};

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-xl border border-gray-200 bg-white px-6 py-16">
      <Spinner label="Loading applications" />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 px-6 py-20 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#f5f7fa] text-sm text-[#11486b]">
        0
      </div>
      <h3 className="mt-5 text-lg font-semibold text-[#11486b]">No Applications Yet</h3>
      <p className="mt-2 max-w-sm text-sm text-gray-500">
        You haven&apos;t applied to any internships yet. Browse recommendations on the home page to
        find your perfect match and start applying.
      </p>
      <Link href="/#recommendations" className="mt-5">
        <Button variant="primary">Explore Internships</Button>
      </Link>
    </div>
  );
}

export default function ApplicationList({
  applications,
  isLoading = false,
  error = null,
  onRetry,
}: ApplicationListProps) {
  if (isLoading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <div className="rounded-xl border border-[#ac2b49] bg-white px-6 py-5 text-center">
        <p className="text-sm font-medium text-[#ac2b49]">{error}</p>
        <p className="mt-1 text-xs text-gray-500">Please try again or contact support.</p>
        {onRetry && (
          <div className="mt-4">
            <Button variant="primary" onClick={onRetry}>
              Retry
            </Button>
          </div>
        )}
      </div>
    );
  }

  if (applications.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      {applications.map((app) => (
        <ApplicationCard key={app.id} application={app} />
      ))}
    </div>
  );
}
