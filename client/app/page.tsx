'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import Link from 'next/link';
import { useState, useMemo } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { useAuth } from '@/hooks/useAuth';
import { useTranslation } from '@/hooks/useTranslation';
import applicationService from '@/services/application.service';
import RecommendationForm, {
  type RecommendationFormData,
} from '@/features/recommendation/RecommendationForm';
import RecommendationList from '@/features/recommendation/RecommendationList';
import recommendationService, { type Recommendation } from '@/services/recommendation.service';

const highlights = [
  {
    title: 'Verified Opportunities',
    description: 'Screened for credibility and safety.',
    icon: (
      <svg className="h-5 w-5 text-[#11486b]" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l7 4v5c0 5-3.5 9.5-7 11-3.5-1.5-7-6-7-11V6l7-4zm-1 12l5-5-1.4-1.4L11 11.2 9.4 9.6 8 11l3 3z" />
      </svg>
    ),
  },
  {
    title: 'Smart Recommendations',
    description: 'Matched to your profile and skills.',
    icon: (
      <svg className="h-5 w-5 text-[#da6328]" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l2.1 5.5L20 9l-4 4 .9 6-5-3-5 3 .9-6-4-4 5.9-1.5L12 2z" />
      </svg>
    ),
  },
  {
    title: 'Application Tracking',
    description: 'Monitor all status updates in one place.',
    icon: (
      <svg className="h-5 w-5 text-[#478356]" viewBox="0 0 24 24" fill="currentColor">
        <path d="M4 5h16v14H4z" opacity="0.2" />
        <path d="M8 9h8v2H8V9zm0 4h5v2H8v-2zm12-8H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H4V7h16v14z" />
      </svg>
    ),
  },
];

export default function HomePage() {
  const { role, isAuthenticated } = useAuth();
  const { t } = useTranslation();
  const isStudent = isAuthenticated && role === 'student';
  const [results, setResults] = useState<Recommendation[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const applicationsQuery = useQuery({
    queryKey: ['my-applications'],
    queryFn: () => applicationService.getMyApplications(),
    enabled: isStudent,
  });

  const appliedIds = useMemo(() => {
    return new Set(applicationsQuery.data?.map((app) => app.internship_id) ?? []);
  }, [applicationsQuery.data]);

  const mutation = useMutation({
    mutationFn: (data: RecommendationFormData) => recommendationService.analyzeResume(data.file),
    onSuccess: (response) => {
      setResults(response);
      setHasSearched(true);
    },
    onError: () => {
      setResults([]);
      setHasSearched(true);
    },
  });

  const errorMessage =
    mutation.error instanceof AxiosError
      ? (mutation.error.response?.data?.detail ?? 'Failed to fetch recommendations.')
      : mutation.error
        ? 'An unexpected error occurred.'
        : null;

  return (
    <div className="space-y-16 pb-16">
      <section className="rounded-2xl bg-[linear-gradient(135deg,#11486b,#1c5d85)] py-20 text-center text-white">
        <div className="mx-auto max-w-3xl space-y-4 px-4">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/70">
            {t('gov.title')}
          </p>
          <h1 className="text-4xl font-bold leading-tight md:text-5xl">
            {t('hero.title')}
          </h1>
          <p className="text-base text-white/80 md:text-lg">
            {t('hero.subtitle')}
          </p>
          <div className="flex justify-center">
            <Link href="/#recommendations">
              <Button variant="primary" className="px-6 py-3 text-sm font-semibold">
                Get Recommendations
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <section id="recommendations" className="rounded-2xl bg-white py-16 shadow-sm">
        <div className="mx-auto max-w-3xl space-y-6 px-4">
          <Card className="p-8">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-[#11486b]">Resume Analyzer</h2>
              <p className="mt-1 text-sm text-gray-500">
                Upload your resume to receive tailored recommendations.
              </p>
            </div>
            <RecommendationForm
              onSubmit={(data) => mutation.mutate(data)}
              isLoading={mutation.isPending}
            />
          </Card>

          {(hasSearched || mutation.isPending) && (
            <RecommendationList
              recommendations={results}
              appliedIds={appliedIds}
              isLoading={mutation.isPending}
              error={errorMessage}
            />
          )}
        </div>
      </section>

      <section className="rounded-2xl bg-gray-50 py-16">
        <div className="mx-auto max-w-7xl space-y-10 px-4">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-[#11486b]">Why use this portal</h2>
            <p className="mt-2 text-sm text-gray-500">
              A single place to discover, apply, and track internships across India.
            </p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {highlights.map((item) => (
              <Card key={item.title} hoverable className="flex flex-col gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm">
                  {item.icon}
                </div>
                <div>
                  <h3 className="text-base font-semibold text-[#11486b]">{item.title}</h3>
                  <p className="mt-1 text-sm text-gray-500">{item.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
