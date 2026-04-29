import type { Recommendation } from '@/services/recommendation.service';

import Spinner from '@/components/ui/Spinner';
import RecommendationCard from './components/RecommendationCard';

type RecommendationListProps = {
  recommendations: Recommendation[];
  appliedIds?: Set<number>;
  isLoading?: boolean;
  error?: string | null;
};

function LoadingState() {
  return (
    <div className="flex items-center justify-center rounded-xl border border-gray-200 bg-white px-6 py-16">
      <Spinner label="Loading recommendations" />
    </div>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-gray-200 bg-gray-50 px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[#f5f7fa] text-sm text-[#11486b]">
        0
      </div>
      <h3 className="mt-4 text-lg font-semibold text-[#11486b]">No Results Found</h3>
      <p className="mt-2 max-w-sm text-sm text-gray-500">
        Upload a resume with clear skills and experience to discover matching internships.
      </p>
    </div>
  );
}

function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-[#ac2b49] bg-white px-6 py-5 text-center">
      <p className="text-sm font-medium text-[#ac2b49]">{message}</p>
      <p className="mt-1 text-xs text-gray-500">
        Please try again or contact support if the issue persists.
      </p>
    </div>
  );
}

export default function RecommendationList({
  recommendations,
  appliedIds = new Set(),
  isLoading = false,
  error = null,
}: RecommendationListProps) {
  if (isLoading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (recommendations.length === 0) {
    return <EmptyState />;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-[#11486b]">Recommended Internships</h3>
        <span className="rounded-full border border-gray-200 bg-[#f5f7fa] px-3 py-1 text-xs font-semibold text-gray-600">
          {recommendations.length} matches
        </span>
      </div>

      {recommendations.map((rec) => (
        <RecommendationCard 
          key={rec.internship_id} 
          recommendation={rec} 
          appliedIds={appliedIds}
        />
      ))}
    </div>
  );
}
