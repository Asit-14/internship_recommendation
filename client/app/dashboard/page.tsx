'use client';

import { useQuery } from '@tanstack/react-query';
import Link from 'next/link';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import userService from '@/services/user.service';
import applicationService from '@/services/application.service';

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

  const applicationsQuery = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => applicationService.getMyApplications(),
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

  const applications = applicationsQuery.data ?? [];
  const recentApplications = applications.slice(0, 3);
  
  const isProfileComplete = Boolean(
    profileQuery.data?.skills?.length && 
    profileQuery.data?.education && 
    profileQuery.data?.phone
  );

  return (
    <AuthGuard allowedRoles={['student']} unauthorizedRedirectTo="/admin">
      <div className="space-y-8">
        <PageHeader
          title={`Welcome back, ${displayName}`}
          meta={roleBadge}
          description="Review your applications and keep your profile up to date."
        />

        <div className="grid gap-6 sm:grid-cols-3">
          <Card className="flex flex-col items-center justify-center text-center p-6">
            <h3 className="text-sm font-semibold uppercase text-gray-500">Total Applications</h3>
            <p className="mt-2 text-3xl font-bold text-[#11486b]">{applications.length}</p>
          </Card>
          
          <Card className="flex flex-col items-center justify-center text-center p-6">
            <h3 className="text-sm font-semibold uppercase text-gray-500">Profile Status</h3>
            <p className={`mt-2 text-xl font-bold ${isProfileComplete ? 'text-[#478356]' : 'text-[#da6328]'}`}>
              {isProfileComplete ? 'Complete' : 'Incomplete'}
            </p>
            {!isProfileComplete && (
              <Link href="/profile" className="mt-2 text-xs text-[#11486b] hover:underline">
                Complete Profile
              </Link>
            )}
          </Card>

          <Card className="flex flex-col items-center justify-center text-center p-6">
            <h3 className="text-sm font-semibold uppercase text-gray-500">Quick Action</h3>
            <Link href="/internships" className="mt-4">
              <Button variant="primary" className="text-xs">Find Internships</Button>
            </Link>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card title="Recent Applications">
            {recentApplications.length === 0 ? (
              <div className="py-6 text-center">
                <p className="text-sm text-gray-500">No applications yet.</p>
                <Link href="/internships" className="mt-4 inline-block">
                  <Button variant="secondary" className="text-xs">Browse Internships</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentApplications.map(app => (
                  <div key={app.id} className="flex justify-between items-center p-3 border border-gray-100 rounded-md">
                    <div>
                      <h4 className="font-medium text-[#11486b] text-sm">{app.internship_title || 'Internship'}</h4>
                      <p className="text-xs text-gray-500">{app.company_name || 'Company'}</p>
                    </div>
                    <span className="text-xs px-2 py-1 bg-gray-100 rounded-md">{app.status}</span>
                  </div>
                ))}
                {applications.length > 3 && (
                  <Link href="/applications" className="block text-center text-xs text-[#11486b] hover:underline mt-2">
                    View all applications
                  </Link>
                )}
              </div>
            )}
          </Card>

          <Card title="Recommended Actions">
             <div className="space-y-3">
               {studentActions.map(action => (
                 <Link key={action.title} href={action.href} className="block p-3 border border-gray-100 rounded-md hover:bg-gray-50 transition">
                   <h4 className="font-medium text-[#11486b] text-sm">{action.title}</h4>
                   <p className="text-xs text-gray-500">{action.description}</p>
                 </Link>
               ))}
             </div>
          </Card>
        </div>
      </div>
    </AuthGuard>
  );
}
