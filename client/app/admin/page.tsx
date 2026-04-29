'use client';

import Link from 'next/link';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Card from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';

export default function AdminPage() {
  const { role } = useAuth();

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
              title: 'Analytics',
              desc: 'Monitor platform usage and performance trends.',
              href: '/admin/analytics',
            },
          ].map((item) => (
            <Link key={item.title} href={item.href}>
              <Card title={item.title} hoverable>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AuthGuard>
  );
}
