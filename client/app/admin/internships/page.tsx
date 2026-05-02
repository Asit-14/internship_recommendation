'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import Table from '@/components/ui/Table';
import Modal from '@/components/ui/Modal';
import adminService from '@/services/admin.service';
import { showError, showSuccess } from '@/lib/toast';
import { Internship } from '@/services/internship.service';

const readErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

export default function AdminInternshipsPage() {
  const queryClient = useQueryClient();
  const [internshipToDelete, setInternshipToDelete] = useState<Internship | null>(null);

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-internships'],
    queryFn: () => adminService.getInternships(),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => adminService.deleteInternship(id),
    onSuccess: () => {
      showSuccess('Internship deleted successfully.');
      queryClient.invalidateQueries({ queryKey: ['admin-internships'] });
      setInternshipToDelete(null);
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to delete internship.'));
      setInternshipToDelete(null);
    },
  });

  const internships = data ?? [];
  const errorMessage = error ? readErrorMessage(error, 'Failed to load internships.') : null;

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Manage Internships"
          description="Review all internships and remove listings when needed."
        />

        {isLoading ? (
          <Card>
            <Spinner label="Loading internships" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : (
          <Table columns={['Title', 'Company', 'Location', 'Status', 'Actions']}>
            {internships.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-500">
                  No internships available.
                </td>
              </tr>
            ) : (
              internships.map((internship) => (
                <tr key={internship.id} className="text-sm text-gray-600">
                  <td className="px-4 py-3 font-medium text-[#11486b]">{internship.title}</td>
                  <td className="px-4 py-3">{internship.company_name}</td>
                  <td className="px-4 py-3">{internship.location}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${
                        internship.is_active
                          ? 'border-[#478356] bg-[#eef6f0] text-[#478356]'
                          : 'border-gray-200 bg-gray-50 text-gray-500'
                      }`}
                    >
                      {internship.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Button
                      variant="danger"
                      className="text-xs"
                      onClick={() => setInternshipToDelete(internship as Internship)}
                    >
                      Delete
                    </Button>
                  </td>
                </tr>
              ))
            )}
          </Table>
        )}
        
        <Modal
          isOpen={!!internshipToDelete}
          onClose={() => setInternshipToDelete(null)}
          title="Delete Internship"
          variant="danger"
          footer={
            <>
              <Button variant="secondary" onClick={() => setInternshipToDelete(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                isLoading={deleteMutation.isPending}
                onClick={() => internshipToDelete && deleteMutation.mutate(internshipToDelete.id)}
              >
                Delete Internship
              </Button>
            </>
          }
        >
          <p>
            Are you sure you want to delete the internship{' '}
            <span className="font-semibold text-gray-900">{internshipToDelete?.title}</span>? This action cannot be undone.
          </p>
        </Modal>
      </div>
    </AuthGuard>
  );
}
