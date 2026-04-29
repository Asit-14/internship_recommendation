'use client';

import Link from 'next/link';

import { useQuery } from '@tanstack/react-query';
import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import { useAuth } from '@/hooks/useAuth';
import adminService from '@/services/admin.service';

export default function AdminPage() {
  const { role } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ['admin-analytics-overview'],
    queryFn: () => adminService.getAnalyticsOverview(),
  });

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Admin Panel"
          description="Manage portal content, internships, and reports."
          meta={
            <span className="inline-flex items-center rounded-full border border-gray-200 bg-[#f5f7fa] px-2.5 py-0.5 text-xs font-semibold text-gray-600">
              {role ?? 'admin'}
            </span>
          }
        />

        {isLoading ? (
           <Card><Spinner label="Loading Overview" /></Card>
        ) : data ? (
           <div className="grid gap-6 sm:grid-cols-3">
             <Card className="flex flex-col items-center justify-center text-center p-6">
               <h3 className="text-sm font-semibold uppercase text-gray-500">Total Users</h3>
               <p className="mt-2 text-3xl font-bold text-[#11486b]">{data.total_users}</p>
             </Card>
             <Card className="flex flex-col items-center justify-center text-center p-6">
               <h3 className="text-sm font-semibold uppercase text-gray-500">Total Internships</h3>
               <p className="mt-2 text-3xl font-bold text-[#11486b]">{data.total_internships}</p>
             </Card>
             <Card className="flex flex-col items-center justify-center text-center p-6">
               <h3 className="text-sm font-semibold uppercase text-gray-500">Total Applications</h3>
               <p className="mt-2 text-3xl font-bold text-[#11486b]">{data.total_applications}</p>
             </Card>
           </div>
        ) : null}

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              title: 'Manage Companies',
              desc: 'Approve and review registered company accounts.',
              href: '/admin/companies',
            },
            {
              title: 'Manage Internships',
              desc: 'Review all listings and remove inappropriate posts.',
              href: '/admin/internships',
            },
            {
              title: 'Manage Users',
              desc: 'Review all registered users.',
              href: '/admin/users',
            },
            {
              title: 'Analytics',
              desc: 'Monitor platform usage and performance trends.',
              href: '/admin/analytics',
            },
          ].map((item) => (
            <Link key={item.title} href={item.href}>
              <Card title={item.title} hoverable className="h-full">
                <p className="text-sm text-gray-500">{item.desc}</p>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AuthGuard>
  );
}
