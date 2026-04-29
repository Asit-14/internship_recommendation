'use client';

import { useQuery } from '@tanstack/react-query';
import { AxiosError } from 'axios';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import adminService from '@/services/admin.service';

const readErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

const buildLinePoints = (values: number[], width: number, height: number, padding: number) => {
  if (values.length === 0) {
    return '';
  }

  const maxValue = Math.max(...values, 1);
  const xStep = values.length > 1 ? (width - padding * 2) / (values.length - 1) : 0;

  return values
    .map((value, index) => {
      const x = padding + index * xStep;
      const y = height - padding - (value / maxValue) * (height - padding * 2);
      return `${x},${y}`;
    })
    .join(' ');
};

export default function AdminAnalyticsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin-analytics'],
    queryFn: () => adminService.getAnalyticsOverview(),
  });

  const errorMessage = error ? readErrorMessage(error, 'Failed to load analytics data.') : null;

  const monthlyStats = data?.monthly_stats ?? [];
  const sectorDistribution = data?.sector_distribution ?? [];

  const userSeries = monthlyStats.map((item) => item.users);
  const applicationSeries = monthlyStats.map((item) => item.applications);

  const chartWidth = 600;
  const chartHeight = 220;
  const padding = 24;
  const userPoints = buildLinePoints(userSeries, chartWidth, chartHeight, padding);
  const applicationPoints = buildLinePoints(applicationSeries, chartWidth, chartHeight, padding);

  const maxSectorCount = Math.max(...sectorDistribution.map((item) => item.count), 1);
  const widthClasses = ['w-1/5', 'w-2/5', 'w-3/5', 'w-4/5', 'w-full'] as const;

  const getSectorWidthClass = (count: number) => {
    if (maxSectorCount <= 0) {
      return widthClasses[0];
    }

    const ratio = count / maxSectorCount;
    const bucket = Math.min(
      widthClasses.length - 1,
      Math.max(0, Math.ceil(ratio * widthClasses.length) - 1),
    );

    return widthClasses[bucket];
  };

  return (
    <AuthGuard allowedRoles={['admin']}>
      <div className="space-y-8">
        <PageHeader
          title="Analytics"
          description="Review portal activity, internship performance, and growth trends."
        />

        {isLoading ? (
          <Card>
            <Spinner label="Loading analytics" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : !data ? (
          <Card>
            <p className="text-sm text-gray-500">No analytics data available.</p>
          </Card>
        ) : (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: 'Total Users', value: data.total_users },
                { label: 'Students', value: data.total_students },
                { label: 'Companies', value: data.total_companies },
                { label: 'Internships', value: data.total_internships },
                { label: 'Applications', value: data.total_applications },
                { label: 'Success Rate', value: `${data.success_rate}%` },
              ].map((metric) => (
                <Card key={metric.label}>
                  <p className="text-xs font-semibold uppercase text-gray-500">{metric.label}</p>
                  <p className="mt-2 text-2xl font-bold text-[#11486b]">{metric.value}</p>
                </Card>
              ))}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <Card title="Sector Distribution">
                {sectorDistribution.length === 0 ? (
                  <p className="text-sm text-gray-500">No sector data available.</p>
                ) : (
                  <div className="space-y-3">
                    {sectorDistribution.map((item) => (
                      <div key={item.sector} className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium text-gray-600">{item.sector}</span>
                          <span className="text-gray-500">{item.count}</span>
                        </div>
                        <div className="h-2 w-full rounded-full bg-gray-200">
                          <div
                            className={`h-2 rounded-full bg-[#da6328] ${getSectorWidthClass(item.count)}`}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </Card>

              <Card title="Monthly Growth">
                {monthlyStats.length === 0 ? (
                  <p className="text-sm text-gray-500">No monthly trend data available.</p>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <span className="inline-flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-[#11486b]" /> Users
                      </span>
                      <span className="inline-flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-[#da6328]" /> Applications
                      </span>
                    </div>
                    <div className="w-full overflow-x-auto">
                      <svg
                        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                        className="h-56 w-full"
                        role="img"
                        aria-label="Monthly growth chart"
                      >
                        <polyline
                          points={userPoints}
                          fill="none"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="stroke-[#11486b]"
                        />
                        <polyline
                          points={applicationPoints}
                          fill="none"
                          strokeWidth="3"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          className="stroke-[#da6328]"
                        />
                      </svg>
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                      {monthlyStats.map((item) => (
                        <span key={item.month}>{item.month}</span>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            </div>
          </div>
        )}
      </div>
    </AuthGuard>
  );
}
