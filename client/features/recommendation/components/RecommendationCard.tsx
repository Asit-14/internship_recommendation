'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import Link from 'next/link';
import { useMemo, useState } from 'react';

import Button from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';
import applicationService from '@/services/application.service';
import type { Recommendation } from '@/services/recommendation.service';

type RecommendationCardProps = {
  recommendation: Recommendation;
  appliedIds?: Set<number>;
};

function MatchScoreBadge({ score }: { score: number }) {
  const percentage = Math.round(score);

  let colorClasses: string;
  if (percentage >= 80) {
    colorClasses = 'bg-[#478356] text-white border-[#478356]';
  } else if (percentage >= 60) {
    colorClasses = 'bg-[#ffa425] text-black border-[#ffa425]';
  } else {
    colorClasses = 'bg-[#ac2b49] text-white border-[#ac2b49]';
  }

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-bold ${colorClasses}`}
    >
      <svg className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
      </svg>
      {percentage}% match
    </span>
  );
}

export default function RecommendationCard({
  recommendation,
  appliedIds = new Set(),
}: RecommendationCardProps) {
  const { role, isAuthenticated } = useAuth();
  const queryClient = useQueryClient();
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const resolvedRole = useMemo(() => (isAuthenticated ? role : null), [isAuthenticated, role]);
  const missingSkills = recommendation.missing_skills ?? recommendation.skill_gap ?? [];

  const isAlreadyApplied = appliedIds.has(recommendation.internship_id);
  const canApply = resolvedRole === 'student';

  const applyMutation = useMutation({
    mutationFn: () => applicationService.applyToInternship(recommendation.internship_id),
    onSuccess: () => {
      setSuccessMsg('Applied Successfully!');
      setErrorMsg(null);
      queryClient.invalidateQueries({ queryKey: ['my-applications'] });
    },
    onError: (err: unknown) => {
      setSuccessMsg(null);
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        setErrorMsg(typeof detail === 'string' ? detail : 'Failed to apply. Please try again.');
      } else {
        setErrorMsg('Something went wrong. Please try again.');
      }
    },
  });

  const hasApplied = isAlreadyApplied || applyMutation.isSuccess;

  return (
    <div className="group rounded-xl border border-gray-200 bg-white p-6 shadow-sm transition hover:shadow-md">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-lg font-semibold text-[#11486b]">{recommendation.title}</h3>
            <MatchScoreBadge score={recommendation.match_score} />
          </div>

          <p className="mt-1 flex items-center gap-1.5 text-sm text-gray-600">
            <svg
              className="h-4 w-4 shrink-0 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21"
              />
            </svg>
            {recommendation.company_name}
          </p>

          <p className="mt-2 text-sm leading-relaxed text-gray-500">{recommendation.explanation}</p>

          <div className="mt-3 flex flex-wrap gap-2">
            {recommendation.sector && (
              <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
                {recommendation.sector}
              </span>
            )}
            {recommendation.location && (
              <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
                📍 {recommendation.location}
              </span>
            )}
            {recommendation.matched_skills.length > 0 && (
              <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600">
                ✓ {recommendation.matched_skills.length} skills matched
              </span>
            )}
          </div>

          {(recommendation.matched_skills.length > 0 || missingSkills.length > 0) && (
            <div className="mt-3 space-y-2 text-xs text-gray-600">
              {recommendation.matched_skills.length > 0 && (
                <div>
                  <span className="font-semibold text-[#11486b]">Matched skills:</span>{' '}
                  {recommendation.matched_skills.slice(0, 5).join(', ')}
                </div>
              )}
              {missingSkills.length > 0 && (
                <div>
                  <span className="font-semibold text-[#11486b]">Missing skills:</span>{' '}
                  {missingSkills.slice(0, 5).join(', ')}
                </div>
              )}
            </div>
          )}

          {successMsg && (
            <p className="mt-3 flex items-center gap-1.5 text-xs font-semibold text-[#478356]">
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {successMsg}
            </p>
          )}
          {errorMsg && <p className="mt-3 text-xs font-medium text-[#ac2b49]">{errorMsg}</p>}
        </div>

        <div className="shrink-0 sm:self-center">
          {!canApply ? (
            resolvedRole === 'admin' ? (
              <span className="inline-flex items-center rounded-md border border-gray-200 bg-gray-50 px-4 py-2.5 text-xs font-semibold text-gray-600">
                Admin accounts cannot apply
              </span>
            ) : resolvedRole === 'company' ? (
              <span className="inline-flex items-center rounded-md border border-gray-200 bg-gray-50 px-4 py-2.5 text-xs font-semibold text-gray-600">
                Company accounts cannot apply
              </span>
            ) : (
              <Link href="/login">
                <Button variant="secondary" className="text-xs">
                  Sign in to apply
                </Button>
              </Link>
            )
          ) : hasApplied ? (
            <span className="inline-flex items-center gap-1.5 rounded-md border border-[#478356] bg-white px-4 py-2.5 text-xs font-semibold text-[#478356]">
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
              Applied
            </span>
          ) : (
            <Button
              variant="primary"
              className="text-xs"
              isLoading={applyMutation.isPending}
              onClick={() => applyMutation.mutate()}
            >
              Apply Now
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
