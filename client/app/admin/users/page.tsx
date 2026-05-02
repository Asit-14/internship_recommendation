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
  if (!user.is_active) {
    return { label: 'Inactive', className: 'border-gray-300 bg-gray-50 text-gray-500' };
  }

  if (user.role !== 'company') {
    return { label: 'Active', className: 'border-[#478356] bg-[#eef6f0] text-[#478356]' };
  }

  if (user.is_verified) {
    return { label: 'Verified', className: 'border-[#11486b] bg-[#f0f5f9] text-[#11486b]' };
  }

  return { label: 'Pending', className: 'border-[#ffa425] bg-[#fffcf5] text-[#da6328]' };
};

export default function AdminUsersPage() {
  const queryClient = useQueryClient();
  const [userToDelete, setUserToDelete] = useState<AdminUser | null>(null);
  const [filterRole, setFilterRole] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

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

  const statusMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number, is_active: boolean }) => adminService.setUserStatus(id, is_active),
    onSuccess: (_, variables) => {
      showSuccess(`User ${variables.is_active ? 'activated' : 'deactivated'} successfully.`);
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
    onError: (error) => {
      showError(getErrorMessage(error, 'Failed to update user status.'));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: number) => adminService.deleteUser(userId),
    onSuccess: () => {
      showSuccess('User deleted successfully.');
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setUserToDelete(null);
    },
    onError: (error) => {
      showError(getErrorMessage(error, 'Failed to delete user.'));
      setUserToDelete(null);
    },
  });

  const users = data ?? [];
  const errorMessage = error
    ? getErrorMessage(error, 'Failed to load users. Please try again.')
    : null;

  const filteredUsers = users.filter((user) => {
    if (filterRole !== 'all' && user.role !== filterRole) return false;
    
    if (filterStatus !== 'all') {
      const status = getStatusLabel(user).label.toLowerCase();
      if (status !== filterStatus) return false;
    }
    
    return true;
  });

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Manage Users"
          description="Approve company accounts and manage all registered users."
        />

        <div className="flex gap-4">
          <select 
            className="border-gray-300 rounded-md shadow-sm text-sm"
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
          >
            <option value="all">All Roles</option>
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
          <select 
            className="border-gray-300 rounded-md shadow-sm text-sm"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="verified">Verified</option>
            <option value="pending">Pending</option>
          </select>
        </div>

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
            {filteredUsers.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-sm text-gray-500">
                  No users found matching criteria.
                </td>
              </tr>
            ) : (
              filteredUsers.map((user) => {
                const status = getStatusLabel(user);
                return (
                  <tr key={user.id} className="text-sm text-gray-600">
                    <td className="px-4 py-3 font-medium text-[#11486b]">{user.name}</td>
                    <td className="px-4 py-3">{user.email}</td>
                    <td className="px-4 py-3 capitalize">{user.role}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${status.className}`}
                      >
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-2">
                        {user.role === 'company' && !user.is_verified && user.is_active && (
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
                          variant="secondary"
                          className="text-xs"
                          isLoading={statusMutation.isPending}
                          onClick={() => statusMutation.mutate({ id: user.id, is_active: !user.is_active })}
                        >
                          {user.is_active ? 'Deactivate' : 'Activate'}
                        </Button>
                        <Button
                          variant="danger"
                          className="text-xs"
                          onClick={() => setUserToDelete(user)}
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
        
        <Modal
          isOpen={!!userToDelete}
          onClose={() => setUserToDelete(null)}
          title="Delete User"
          variant="danger"
          footer={
            <>
              <Button variant="secondary" onClick={() => setUserToDelete(null)}>
                Cancel
              </Button>
              <Button
                variant="danger"
                isLoading={deleteMutation.isPending}
                onClick={() => userToDelete && deleteMutation.mutate(userToDelete.id)}
              >
                Delete User
              </Button>
            </>
          }
        >
          <p>
            Are you sure you want to delete the user{' '}
            <span className="font-semibold text-gray-900">{userToDelete?.name}</span>? This action cannot be undone.
          </p>
        </Modal>
      </div>
    </AuthGuard>
  );
}
