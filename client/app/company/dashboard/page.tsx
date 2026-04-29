'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import Link from 'next/link';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import Table from '@/components/ui/Table';
import { useAuth } from '@/hooks/useAuth';
import internshipService from '@/services/internship.service';

const readErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

export default function CompanyDashboardPage() {
  const queryClient = useQueryClient();
  const { isVerified } = useAuth();

  const { data, isLoading, error } = useQuery({
    queryKey: ['company-internships'],
    queryFn: () => internshipService.getCompanyInternships(),
    enabled: isVerified !== false,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => internshipService.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['company-internships'] }),
  });

  const internships = data ?? [];
  const errorMessage = error ? readErrorMessage(error, 'Failed to load internships.') : null;
  const isPendingApproval = isVerified === false;

  return (
    <AuthGuard allowedRoles={['company']}>
      <div className="space-y-8">
        <PageHeader
          title="Company Dashboard"
          description="Manage your internship listings and track approvals."
          actions={
            <Link href="/company/create-internship">
              <Button variant="primary" className="text-xs" disabled={isPendingApproval}>
                Create Internship
              </Button>
            </Link>
          }
        />

        {isPendingApproval && (
          <Card>
            <p className="text-sm font-medium text-gray-600">
              Your company account is pending approval. You can manage listings after approval.
            </p>
          </Card>
        )}

        {isLoading ? (
          <Card>
            <Spinner label="Loading internships" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : (
          <Table columns={['Title', 'Location', 'Status', 'Actions']}>
            {internships.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-500">
                  No internships created yet.
                </td>
              </tr>
            ) : (
              internships.map((internship) => (
                <tr key={internship.id} className="text-sm text-gray-600">
                  <td className="px-4 py-3 font-medium text-[#11486b]">{internship.title}</td>
                  <td className="px-4 py-3">{internship.location}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full border bg-[#f5f7fa] px-2.5 py-0.5 text-xs font-semibold ${
                        internship.is_active
                          ? 'border-[#478356] text-[#478356]'
                          : 'border-gray-200 text-gray-500'
                      }`}
                    >
                      {internship.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex flex-wrap gap-2">
                      <Link href={`/company/edit-internship/${internship.id}`}>
                        <Button
                          variant="secondary"
                          className="text-xs"
                          disabled={isPendingApproval}
                        >
                          Edit
                        </Button>
                      </Link>
                      <Button
                        variant="danger"
                        className="text-xs"
                        isLoading={deleteMutation.isPending}
                        disabled={isPendingApproval}
                        onClick={() => {
                          const confirmed = window.confirm(
                            `Delete ${internship.title}? This cannot be undone.`,
                          );
                          if (confirmed) {
                            deleteMutation.mutate(internship.id);
                          }
                        }}
                      >
                        Delete
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </Table>
        )}
      </div>
    </AuthGuard>
  );
}
