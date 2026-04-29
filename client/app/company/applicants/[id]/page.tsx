'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { useParams } from 'next/navigation';
import { useMemo, useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import Table from '@/components/ui/Table';
import StatusBadge from '@/features/application/StatusBadge';
} from '@/services/application.service';
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

const allowedStatusTransitions: Record<ApplicationStatus, ApplicationStatus[]> = {
  APPLIED: ['UNDER_REVIEW', 'REJECTED'],
  UNDER_REVIEW: ['SHORTLISTED', 'SELECTED', 'REJECTED'],
  SHORTLISTED: ['SELECTED', 'REJECTED'],
  SELECTED: ['REJECTED'],
  IN_PROGRESS: [],
  REJECTED: [],
  COMPLETED: [],
};

export default function CompanyApplicantsPage() {
  const params = useParams();
  const queryClient = useQueryClient();
  const internshipId = Number(params?.id);

  const [manualSelectedId, setManualSelectedId] = useState<number | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const applicantsQuery = useQuery({
    queryKey: ['company-applicants', internshipId],
    queryFn: () => applicationService.getApplicantsByInternship(internshipId),
    enabled: Number.isFinite(internshipId),
  });

  const applicants = useMemo(() => applicantsQuery.data ?? [], [applicantsQuery.data]);

  const selectedApplicationId = useMemo(() => {
    if (manualSelectedId) {
      const exists = applicants.some((item) => item.application_id === manualSelectedId);
      if (exists) {
        return manualSelectedId;
      }
    }

    return applicants[0]?.application_id ?? null;
  }, [applicants, manualSelectedId]);

  const selectedApplicant = useMemo(
    () => applicants.find((item) => item.application_id === selectedApplicationId) ?? null,
    [applicants, selectedApplicationId],
  );

  const detailQuery = useQuery({
    queryKey: ['application-detail', selectedApplicationId],
    queryFn: () => applicationService.getById(selectedApplicationId as number),
    enabled: selectedApplicationId !== null,
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ApplicationStatus }) =>
      applicationService.updateStatus(id, status),
    onSuccess: () => {
      showSuccess('Applicant status updated successfully.');
      queryClient.invalidateQueries({ queryKey: ['company-applicants', internshipId] });
      queryClient.invalidateQueries({ queryKey: ['application-detail', selectedApplicationId] });
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to update status.'));
    },
  });

  const handleStatusChange = (status: ApplicationStatus) => {
    if (!selectedApplicant) {
      return;
    }

    statusMutation.mutate({ id: selectedApplicant.application_id, status });
  };

  const handleResumeDownload = async (detail: ApplicationDetail) => {
    setDownloadError(null);

    try {
      const { blob, filename } = await applicationService.downloadResume(detail.id);
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(blobUrl);
    } catch (error) {
      showError(readErrorMessage(error, 'Failed to download resume.'));
    }
  };

  const applicantsError = applicantsQuery.error
    ? readErrorMessage(applicantsQuery.error, 'Failed to load applicants.')
    : null;

  const detail = detailQuery.data ?? null;
  const detailError = detailQuery.error
    ? readErrorMessage(detailQuery.error, 'Failed to load applicant details.')
    : null;
  const activeStatus = detail?.status ?? selectedApplicant?.status ?? 'APPLIED';
  const canTransitionTo = allowedStatusTransitions[activeStatus] ?? [];

  return (
    <AuthGuard allowedRoles={['company']}>
      <div className="space-y-8">
        <PageHeader
          title="Applicants"
          description="Review applicant profiles, resume links, and update status in real time."
        />

        <div className="grid gap-6 lg:grid-cols-[1.4fr_1fr]">
          <div className="space-y-4">
            {applicantsQuery.isLoading ? (
              <Card>
                <Spinner label="Loading applicants" />
              </Card>
            ) : applicantsError ? (
              <Card>
                <p className="text-sm font-medium text-[#ac2b49]">{applicantsError}</p>
              </Card>
            ) : (
              <Table columns={['Name', 'Skills', 'Education', 'Status', 'Actions']}>
                {applicants.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-500">
                      No applicants yet.
                    </td>
                  </tr>
                ) : (
                  applicants.map((applicant) => (
                    <tr key={applicant.application_id} className="text-sm text-gray-600">
                      <td className="px-4 py-3 font-medium text-[#11486b]">
                        {applicant.student.name}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {applicant.student.skills.length === 0
                            ? '—'
                            : applicant.student.skills.slice(0, 3).map((skill) => (
                                <span
                                  key={skill}
                                  className="rounded-full border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs text-gray-600"
                                >
                                  {skill}
                                </span>
                              ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        {applicant.student.education || 'Education details pending'}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={applicant.status} />
                      </td>
                      <td className="px-4 py-3">
                        <Button
                          variant={
                            applicant.application_id === selectedApplicationId
                              ? 'primary'
                              : 'secondary'
                          }
                          className="text-xs"
                          onClick={() => setManualSelectedId(applicant.application_id)}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </Table>
            )}
          </div>

          <div className="space-y-4">
            <Card>
              {!detailQuery.isLoading && !detail ? (
                <div className="space-y-2">
                  <p className="text-sm text-gray-500">Select an applicant to review.</p>
                </div>
              ) : detailQuery.isLoading ? (
                <Spinner label="Loading applicant details" />
              ) : detailError ? (
                <p className="text-sm font-medium text-[#ac2b49]">{detailError}</p>
              ) : detail ? (
                <div className="space-y-4">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Applicant</p>
                    <h3 className="text-lg font-semibold text-[#11486b]">{detail.student.name}</h3>
                    <p className="text-sm text-gray-600">{detail.student.email}</p>
                    {detail.student.phone && (
                      <p className="text-sm text-gray-600">{detail.student.phone}</p>
                    )}
                    {detail.student.location && (
                      <p className="text-sm text-gray-600">{detail.student.location}</p>
                    )}
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Education</p>
                    <p className="text-sm text-gray-600">
                      {detail.student.education || 'Education not provided'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {detail.student.college_name || 'College not provided'}
                    </p>
                    <p className="text-sm text-gray-600">
                      {detail.student.branch || 'Branch not provided'}
                      {detail.student.graduation_year ? ` • ${detail.student.graduation_year}` : ''}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Skills</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {detail.student.skills.length === 0 ? (
                        <span className="text-sm text-gray-500">No skills listed.</span>
                      ) : (
                        detail.student.skills.map((skill) => (
                          <span
                            key={skill}
                            className="rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600"
                          >
                            {skill}
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Resume</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <Button
                        variant="secondary"
                        className="text-xs"
                        onClick={() => handleResumeDownload(detail)}
                        disabled={!detail.resume_url}
                      >
                        Download Resume
                      </Button>
                      {!detail.resume_url && (
                        <span className="text-xs text-gray-500">Resume not uploaded.</span>
                      )}
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Current Status</p>
                    <div className="mt-2">
                      <StatusBadge status={detail.status} />
                    </div>
                  </div>

                  <div>
                    <p className="text-xs uppercase tracking-wide text-gray-500">Update Status</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Button
                        variant="secondary"
                        className="text-xs"
                        onClick={() => handleStatusChange('UNDER_REVIEW')}
                        disabled={!canTransitionTo.includes('UNDER_REVIEW')}
                        isLoading={statusMutation.isPending}
                      >
                        Under Review
                      </Button>
                      <Button
                        variant="secondary"
                        className="text-xs"
                        onClick={() => handleStatusChange('SHORTLISTED')}
                        disabled={!canTransitionTo.includes('SHORTLISTED')}
                        isLoading={statusMutation.isPending}
                      >
                        Shortlist
                      </Button>
                      <Button
                        variant="secondary"
                        className="text-xs"
                        onClick={() => handleStatusChange('SELECTED')}
                        disabled={!canTransitionTo.includes('SELECTED')}
                        isLoading={statusMutation.isPending}
                      >
                        Select
                      </Button>
                      <Button
                        variant="danger"
                        className="text-xs"
                        onClick={() => handleStatusChange('REJECTED')}
                        disabled={!canTransitionTo.includes('REJECTED')}
                        isLoading={statusMutation.isPending}
                      >
                        Reject
                      </Button>
                    </div>
                  </div>
                </div>
              ) : null}
            </Card>
          </div>
        </div>
      </div>
    </AuthGuard>
  );
}
