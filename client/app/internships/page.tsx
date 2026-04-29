'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { useMemo, useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import InternshipList from '@/features/internship/InternshipList';
import applicationService, { type Application } from '@/services/application.service';
import internshipService from '@/services/internship.service';
import { showError, showSuccess } from '@/lib/toast';

const readErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

export default function InternshipListingPage() {
  const queryClient = useQueryClient();
  const [applyingId, setApplyingId] = useState<number | null>(null);

  const internshipsQuery = useQuery({
    queryKey: ['internships'],
    queryFn: () => internshipService.getAll(),
  });

  const applicationsQuery = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => applicationService.getMyApplications(),
  });

  const applyMutation = useMutation({
    mutationFn: (internshipId: number) => applicationService.applyToInternship(internshipId),
    onSuccess: () => {
      showSuccess('Applied Successfully!');
      setApplyingId(null);
      queryClient.invalidateQueries({ queryKey: ['my-applications'] });
    },
    onError: (error) => {
      setApplyingId(null);
      showError(readErrorMessage(error, 'Failed to apply for this internship.'));
    },
  });

  const internships = internshipsQuery.data ?? [];
  const appliedIds = useMemo(() => {
    const applied = new Set<number>();
    for (const application of applicationsQuery.data ?? []) {
      applied.add(application.internship_id);
    }
    return applied;
  }, [applicationsQuery.data]);

  const applicationsByInternshipId = useMemo(() => {
    const map = new Map<number, Application>();
    for (const application of applicationsQuery.data ?? []) {
      map.set(application.internship_id, application);
    }
    return map;
  }, [applicationsQuery.data]);

  const internshipsError = internshipsQuery.error
    ? readErrorMessage(internshipsQuery.error, 'Failed to load internships.')
    : null;

  return (
    <AuthGuard allowedRoles={['student']} unauthorizedRedirectTo="/login">
      <div className="space-y-8">
        <PageHeader title="Internships" description="Browse verified internships and apply." />

        <InternshipList
          internships={internships}
          isLoading={internshipsQuery.isLoading}
          error={internshipsError}
          onApply={(id) => {
            if (appliedIds.has(id)) {
              return;
            }
            setApplyingId(id);
            applyMutation.mutate(id);
          }}
          applyingId={applyingId}
          appliedIds={appliedIds}
          applicationsByInternshipId={applicationsByInternshipId}
        />
      </div>
    </AuthGuard>
  );
}
