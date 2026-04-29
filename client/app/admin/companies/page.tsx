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
import adminService, { type AdminUser } from '@/services/admin.service';
import { showError, showSuccess } from '@/lib/toast';

const getErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

const getStatusLabel = (company: AdminUser): { label: string; className: string } => {
  if (company.is_verified) {
    return { label: 'Verified', className: 'border-[#478356] bg-[#f5f7fa] text-[#478356]' };
  }

  return { label: 'Pending', className: 'border-[#ffa425] bg-[#f5f7fa] text-[#da6328]' };
};

export default function AdminCompaniesPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-companies'],
    queryFn: () => adminService.getCompanies(),
  });

  const approveMutation = useMutation({
    mutationFn: (companyId: number) => adminService.approveUser(companyId),
    onSuccess: () => {
      showSuccess('Company approved successfully.');
      queryClient.invalidateQueries({ queryKey: ['admin-companies'] });
    },
    onError: (error) => {
      showError(getErrorMessage(error, 'Failed to approve company.'));
    },
  });

  const companies = data ?? [];
  const errorMessage = error
    ? getErrorMessage(error, 'Failed to load companies. Please try again.')
    : null;

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Manage Companies"
          description="Approve company accounts and review their internship activity."
        />

        {isLoading ? (
          <Card>
            <Spinner label="Loading companies" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : (
          <Table columns={['Name', 'Email', 'Status', 'Actions']}>
            {companies.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-sm text-gray-500">
                  No companies registered yet.
                </td>
              </tr>
            ) : (
              companies.map((company) => {
                const status = getStatusLabel(company);
                return (
                  <tr key={company.id} className="text-sm text-gray-600">
                    <td className="px-4 py-3 font-medium text-[#11486b]">{company.name}</td>
                    <td className="px-4 py-3">{company.email}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${status.className}`}
                      >
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {!company.is_verified && (
                          <Button
                            variant="primary"
                            className="text-xs"
                            isLoading={approveMutation.isPending}
                            onClick={() => approveMutation.mutate(company.id)}
                          >
                            Approve
                          </Button>
                        )}
                        <Link href={`/admin/company/${company.id}`}>
                          <Button variant="secondary" className="text-xs">
                            View Details
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </Table>
        )}
      </div>
    </AuthGuard>
  );
}
