'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { useParams } from 'next/navigation';
import { FormEvent, useMemo, useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Spinner from '@/components/ui/Spinner';
import internshipService, {
  type CreateInternshipPayload,
  type Internship,
} from '@/services/internship.service';
import { showError, showSuccess } from '@/lib/toast';

const fieldClassName =
  'w-full rounded-md border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-800 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-[#11486b] focus:ring-2 focus:ring-[#11486b]/20 disabled:cursor-not-allowed disabled:opacity-60';

const parseSkills = (value: string): string[] =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

type InternshipFormState = {
  title: string;
  description: string;
  skills_required: string;
  location: string;
  duration: string;
  stipend: string;
  is_active: boolean;
};

const emptyFormState: InternshipFormState = {
  title: '',
  description: '',
  skills_required: '',
  location: '',
  duration: '',
  stipend: '',
  is_active: true,
};

const toFormState = (internship: Internship): InternshipFormState => ({
  title: internship.title,
  description: internship.description,
  skills_required: internship.skills_required.join(', '),
  location: internship.location,
  duration: String(internship.duration),
  stipend: String(internship.stipend),
  is_active: internship.is_active,
});

export default function CompanyEditInternshipPage() {
  const internshipId = Number(params?.id);

  const [draftFormState, setDraftFormState] = useState<{
    id: number;
    value: InternshipFormState;
  } | null>(null);

  const {
    data,
    isLoading,
    error: fetchError,
  } = useQuery({
    queryKey: ['company-internship', internshipId],
    queryFn: () => internshipService.getById(internshipId),
    enabled: Number.isFinite(internshipId),
  });

  const initialFormState = useMemo(() => (data ? toFormState(data) : emptyFormState), [data]);

  const formState = useMemo(() => {
    if (draftFormState && draftFormState.id === internshipId) {
      return draftFormState.value;
    }

    return initialFormState;
  }, [draftFormState, internshipId, initialFormState]);

  const updateFormState = (updater: (prev: InternshipFormState) => InternshipFormState) => {
    setDraftFormState((prev) => {
      const baseState = prev && prev.id === internshipId ? prev.value : initialFormState;
      return {
        id: internshipId,
        value: updater(baseState),
      };
    });
  };

  const mutation = useMutation({
    mutationFn: (payload: Partial<CreateInternshipPayload>) =>
      internshipService.update(internshipId, payload),
    onSuccess: () => {
      showSuccess('Internship updated successfully.');
    },
    onError: (err: unknown) => {
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        showError(typeof detail === 'string' ? detail : 'Failed to update internship.');
      } else {
        showError('Failed to update internship.');
      }
    },
  });

  const skills = useMemo(() => parseSkills(formState.skills_required), [formState.skills_required]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!skills.length) {
      showError('Please add at least one skill.');
      return;
    }

    const durationValue = Number(formState.duration);
    const stipendValue = Number(formState.stipend);

    if (!Number.isFinite(durationValue) || durationValue <= 0) {
      showError('Duration must be a positive number of weeks.');
      return;
    }

    if (!Number.isFinite(stipendValue) || stipendValue < 0) {
      showError('Stipend must be zero or a positive number.');
      return;
    }

    mutation.mutate({
      title: formState.title.trim(),
      description: formState.description.trim(),
      skills_required: skills,
      location: formState.location.trim(),
      duration: durationValue,
      stipend: stipendValue,
      is_active: formState.is_active,
    });
  };

  const errorMessage = fetchError
    ? fetchError instanceof AxiosError
      ? (fetchError.response?.data?.detail ?? 'Failed to load internship.')
      : 'Failed to load internship.'
    : null;

  return (
    <AuthGuard allowedRoles={['company']}>
      <div className="space-y-8">
        <PageHeader
          title="Edit Internship"
          description="Update details for your internship listing."
        />

        {isLoading ? (
          <Card>
            <Spinner label="Loading internship" />
          </Card>
        ) : errorMessage ? (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">{errorMessage}</p>
          </Card>
        ) : !data ? (
          <Card>
            <p className="text-sm text-gray-500">Internship not found.</p>
          </Card>
        ) : (
          <Card>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <Input
                id="internship-title"
                label="Title"
                value={formState.title}
                onChange={(event) =>
                  updateFormState((prev) => ({ ...prev, title: event.target.value }))
                }
                required
              />

              <div className="flex flex-col gap-1.5">
                <label
                  htmlFor="internship-description"
                  className="text-sm font-semibold text-gray-700"
                >
                  Description
                  <span className="ml-0.5 text-[#da6328]">*</span>
                </label>
                <textarea
                  id="internship-description"
                  value={formState.description}
                  onChange={(event) =>
                    updateFormState((prev) => ({ ...prev, description: event.target.value }))
                  }
                  rows={5}
                  required
                  className={fieldClassName}
                />
              </div>

              <Input
                id="internship-skills"
                label="Skills Required"
                value={formState.skills_required}
                onChange={(event) =>
                  updateFormState((prev) => ({ ...prev, skills_required: event.target.value }))
                }
                required
              />

              <Input
                id="internship-location"
                label="Location"
                value={formState.location}
                onChange={(event) =>
                  updateFormState((prev) => ({ ...prev, location: event.target.value }))
                }
                required
              />

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-1.5">
                  <label
                    htmlFor="internship-duration"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Duration (weeks)
                    <span className="ml-0.5 text-[#da6328]">*</span>
                  </label>
                  <input
                    id="internship-duration"
                    type="number"
                    min={1}
                    value={formState.duration}
                    onChange={(event) =>
                      updateFormState((prev) => ({ ...prev, duration: event.target.value }))
                    }
                    required
                    className={fieldClassName}
                  />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label
                    htmlFor="internship-stipend"
                    className="text-sm font-semibold text-gray-700"
                  >
                    Stipend (monthly)
                    <span className="ml-0.5 text-[#da6328]">*</span>
                  </label>
                  <input
                    id="internship-stipend"
                    type="number"
                    min={0}
                    value={formState.stipend}
                    onChange={(event) =>
                      updateFormState((prev) => ({ ...prev, stipend: event.target.value }))
                    }
                    required
                    className={fieldClassName}
                  />
                </div>
              </div>

              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input
                  type="checkbox"
                  checked={formState.is_active}
                  onChange={(event) =>
                    updateFormState((prev) => ({ ...prev, is_active: event.target.checked }))
                  }
                  className="h-4 w-4 rounded border-gray-300 text-[#11486b] focus:ring-[#11486b]/20"
                />
                Active listing
              </label>

              <Button type="submit" variant="primary" isLoading={mutation.isPending}>
                Save Changes
              </Button>
            </form>
          </Card>
        )}
      </div>
    </AuthGuard>
  );
}
