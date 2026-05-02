'use client';

import { useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import Link from 'next/link';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import userService from '@/services/user.service';
import applicationService from '@/services/application.service';
import certificateService from '@/services/certificate.service';
import { showError } from '@/lib/toast';

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
  const queryClient = useQueryClient();
  const profileQuery = useQuery({
    queryKey: ['user-profile'],
    queryFn: () => userService.getProfile(),
  });

  const applicationsQuery = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => applicationService.getMyApplications(),
  });

  const certificatesQuery = useQuery({
    queryKey: ['my-certificates'],
    queryFn: () => certificateService.getMyCertificates(),
    enabled: role === 'student',
  });

  const handleDownloadCertificate = (certificateUrl: string) => {
    window.open(certificateUrl, '_blank', 'noopener,noreferrer');
  };

  const displayName = profileQuery.data?.name || 'Student';
  const roleLabel = role ?? profileQuery.data?.role ?? 'student';

  const roleBadge = (
    <span className="inline-flex items-center rounded-full border border-gray-200 bg-[#f5f7fa] px-2.5 py-0.5 text-xs font-semibold text-gray-600">
      {roleLabel}
    </span>
  );

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
                {recentApplications.map(app => {
                  const certificate = certificatesQuery.data?.find(c => c.internship_id === app.internship_id);
                  return (
                    <div key={app.id} className="flex justify-between items-center p-3 border border-gray-100 rounded-md bg-white">
                      <div className="min-w-0 flex-1">
                        <h4 className="font-medium text-[#11486b] text-sm truncate">{app.internship_title || 'Internship'}</h4>
                        <p className="text-xs text-gray-500 truncate">{app.company_name || 'Company'}</p>
                      </div>
                      <div className="flex items-center gap-3 ml-4 shrink-0">
                        {app.status === 'COMPLETED' && (
                          certificate ? (
                            <button
                              onClick={() => handleDownloadCertificate(certificate.certificate_url)}
                              title="Download Certificate"
                              className="flex h-8 w-8 items-center justify-center rounded-full bg-green-50 text-green-600 hover:bg-green-100 transition-colors"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                            </button>
                          ) : (
                            <button
                              onClick={async () => {
                                try {
                                  await certificateService.generateMissing(app.id);
                                  await queryClient.invalidateQueries({ queryKey: ['my-certificates'] });
                                  await queryClient.invalidateQueries({ queryKey: ['my-applications'] });
                                } catch (e: unknown) {
                                  // If it already exists, just refresh the queries
                                  if (e instanceof AxiosError && e.response?.status === 409) {
                                    queryClient.invalidateQueries({ queryKey: ['my-certificates'] });
                                  } else {
                                    showError('Failed to sync certificate');
                                  }
                                }
                              }}
                              title="Sync Certificate"
                              className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors animate-pulse"
                            >
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                              </svg>
                            </button>
                          )
                        )}
                        <span className={`text-[10px] px-2 py-0.5 rounded-md font-bold uppercase tracking-wider ${
                          app.status === 'COMPLETED' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {app.status}
                        </span>
                      </div>
                    </div>
                  );
                })}
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

        {certificatesQuery.data && certificatesQuery.data.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-[#11486b]">My Certificates</h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {certificatesQuery.data.map(cert => {
                // Find corresponding internship title from applications
                const app = applications.find(a => a.internship_id === cert.internship_id);
                return (
                  <Card key={cert.id} className="p-4 flex flex-col justify-between">
                    <div>
                      <h4 className="font-bold text-[#11486b] text-sm mb-1">
                        {app?.internship_title || 'Internship Certificate'}
                      </h4>
                      <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">
                        ID: {cert.certificate_id}
                      </p>
                      <p className="text-xs text-gray-600">
                        Issued on: {new Date(cert.issued_at).toLocaleDateString()}
                      </p>
                    </div>
                    <Button 
                      variant="secondary" 
                      className="mt-4 text-xs h-8"
                      onClick={() => handleDownloadCertificate(cert.certificate_url)}
                    >
                      Download PDF
                    </Button>
                  </Card>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
