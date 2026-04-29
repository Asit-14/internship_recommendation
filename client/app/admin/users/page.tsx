'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';

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

const getStatusLabel = (user: AdminUser): { label: string; className: string } => {
  if (user.role !== 'company') {
    return { label: 'Active', className: 'border-[#478356] bg-[#f5f7fa] text-[#478356]' };
  }

  if (user.is_verified) {
    return { label: 'Verified', className: 'border-[#478356] bg-[#f5f7fa] text-[#478356]' };
  }

  return { label: 'Pending', className: 'border-[#ffa425] bg-[#f5f7fa] text-[#da6328]' };
};

export default function AdminUsersPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => adminService.getUsers(),
  });

  const approveMutation = useMutation({
    mutationFn: (userId: number) => adminService.approveUser(userId),
    onSuccess: () => {
      showSuccess('User approved successfully.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (error) => {
      showError(getErrorMessage(error, 'Failed to approve user.'));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: number) => adminService.deleteUser(userId),
    onSuccess: () => {
      showSuccess('User deleted successfully.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (error) => {
      showError(getErrorMessage(error, 'Failed to delete user.'));
    },
  });

  const users = data ?? [];
  const errorMessage = error
    ? getErrorMessage(error, 'Failed to load users. Please try again.')
    : null;

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Manage Users"
          description="Approve company accounts and manage all registered users."
        />

        {isLoading ? (
          <Card>
            <Spinner label="Loading users" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : (
          <Table columns={['Name', 'Email', 'Role', 'Status', 'Actions']}>
            {users.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-500">
                  No users found yet.
                </td>
              </tr>
            ) : (
              users.map((user) => {
                const status = getStatusLabel(user);
                return (
                  <tr key={user.id} className="text-sm text-gray-600">
                    <td className="px-4 py-3 font-medium text-[#11486b]">{user.name}</td>
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3 capitalize">{user.role}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${status.className}`}
                      >
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {user.role === 'company' && !user.is_verified && (
                          <Button
                            variant="secondary"
                            className="text-xs"
                            isLoading={approveMutation.isPending}
                            onClick={() => approveMutation.mutate(user.id)}
                          >
                            Approve
                          </Button>
                        )}
                        <Button
                          variant="danger"
                          className="text-xs"
                          isLoading={deleteMutation.isPending}
                          onClick={() => {
                            const confirmed = window.confirm(
                              `Delete ${user.name}? This cannot be undone.`,
                            );
                            if (confirmed) {
                              deleteMutation.mutate(user.id);
                            }
                          }}
                        >
                          Delete
                        </Button>
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
