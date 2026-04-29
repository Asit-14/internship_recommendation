'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import userService from '@/services/user.service';

const studentActions = [
  {
    title: 'My Applications',
    description: 'Track status of your internship applications',
    href: '/applications',
  },
  {
    title: 'Recommendations',
    description: 'Get AI-powered internship suggestions',
    href: '/#recommendations',
  },
  {
    title: 'Profile Settings',
    description: 'Update your personal information',
    href: '/profile',
  },
];

export default function DashboardPage() {
  const { role } = useAuth();
  const profileQuery = useQuery({
    queryKey: ['user-profile'],
    queryFn: () => userService.getProfile(),
  });

  const displayName = profileQuery.data?.name || 'Student';
  const roleLabel = role ?? profileQuery.data?.role ?? 'student';
  const quickActions = studentActions;

  const roleBadge = (
    <span className="inline-flex items-center rounded-full border border-gray-200 bg-[#f5f7fa] px-2.5 py-0.5 text-xs font-semibold text-gray-600">
      {roleLabel}
    </span>
  );
  const headerDescription =
    role === 'company'
      ? 'Track approvals and manage your internship postings.'
      : 'Review your applications and keep your profile up to date.';

  return (
    <AuthGuard allowedRoles={['student']} unauthorizedRedirectTo="/admin">
      <div className="space-y-10">
        <PageHeader
          title={`Welcome back, ${displayName}`}
          meta={roleBadge}
          description={headerDescription}
        />
        <section>
          <Card title="Recent Activity">
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#f5f7fa] text-sm text-[#11486b]">
                0
              </div>
              <h3 className="mt-4 text-lg font-semibold text-[#11486b]">No activity yet</h3>
              <p className="mt-1 max-w-sm text-sm text-gray-500">
                Start exploring internships and applying to see your activity here.
              </p>
              <Link href="/#recommendations" className="mt-4">
                <Button variant="primary">Explore Internships</Button>
              </Link>
            </div>
          </Card>
        </section>
      </div>
    </AuthGuard>
  );
}
