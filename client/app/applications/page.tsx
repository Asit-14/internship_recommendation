'use client';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import ApplicationList from '@/features/application/ApplicationList';
import applicationService from '@/services/application.service';
import { useQuery } from '@tanstack/react-query';
import { AxiosError } from 'axios';

export default function ApplicationsPage() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => applicationService.getMyApplications(),
  });

  const applications = data ?? [];

  let errorMessage: string | null = null;
  if (error) {
    if (error instanceof AxiosError) {
      const detail = error.response?.data?.detail;
      errorMessage = typeof detail === 'string' ? detail : 'Failed to load applications.';
    } else {
      errorMessage = 'An unexpected error occurred.';
    }
  }

  return (
    <AuthGuard allowedRoles={['student']} unauthorizedRedirectTo="/admin">
      <div className="space-y-8">
        <PageHeader
          title="My Applications"
          description="Track and manage all your internship applications."
        />
        <ApplicationList
          applications={applications}
          isLoading={isLoading}
          error={errorMessage}
          onRetry={refetch}
        />
      </div>
    </AuthGuard>
  );
}
