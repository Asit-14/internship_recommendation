'use client';

import { useMutation } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { FormEvent, useMemo, useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/hooks/useAuth';
import internshipService, { type CreateInternshipPayload } from '@/services/internship.service';

const fieldClassName =
  'w-full rounded-md border border-gray-300 bg-white px-3.5 py-2.5 text-sm text-gray-800 shadow-sm outline-none transition-all duration-200 placeholder:text-gray-400 focus:border-[#11486b] focus:ring-2 focus:ring-[#11486b]/20 disabled:cursor-not-allowed disabled:opacity-60';

const parseSkills = (value: string): string[] =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

export default function CreateInternshipPage() {
  const { isVerified } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [skillsInput, setSkillsInput] = useState('');
  const [location, setLocation] = useState('');
  const [duration, setDuration] = useState('');
  const [stipend, setStipend] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const isPendingApproval = isVerified === false;

  const mutation = useMutation({
    mutationFn: (payload: CreateInternshipPayload) => internshipService.create(payload),
    onSuccess: () => {
      setTitle('');
      setDescription('');
      setSkillsInput('');
      setLocation('');
      setDuration('');
      setStipend('');
      setError(null);
      setSuccess('Internship created successfully.');
    },
    onError: (err: unknown) => {
      setSuccess(null);
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : 'Failed to create internship.');
      } else {
        setError('Failed to create internship.');
      }
    },
  });

  const isSubmitting = mutation.isPending;
  const isDisabled = isPendingApproval || isSubmitting;

  const skills = useMemo(() => parseSkills(skillsInput), [skillsInput]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (isPendingApproval) {
      return;
    }

    setError(null);
    setSuccess(null);

    if (!skills.length) {
      setError('Please add at least one skill.');
      return;
    }

    const durationValue = Number(duration);
    const stipendValue = Number(stipend);

    if (!Number.isFinite(durationValue) || durationValue <= 0) {
      setError('Duration must be a positive number of weeks.');
      return;
    }

    if (!Number.isFinite(stipendValue) || stipendValue < 0) {
      setError('Stipend must be zero or a positive number.');
      return;
    }

    mutation.mutate({
      title: title.trim(),
      description: description.trim(),
      skills_required: skills,
      location: location.trim(),
      duration: durationValue,
      stipend: stipendValue,
    });
  };

  return (
    <AuthGuard allowedRoles={['company']}>
      <div className="space-y-8">
        <PageHeader
          title="Create Internship"
          description="Publish new internship opportunities for students across India."
        />

        {isPendingApproval && (
          <Card>
            <p className="text-sm font-medium text-gray-600">
              Your company account is pending approval. You can submit internships after an admin
              verifies your account.
            </p>
          </Card>
        )}

        <Card>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <Input
              id="internship-title"
              label="Title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="e.g. Frontend Engineering Intern"
              required
              disabled={isDisabled}
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
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Describe responsibilities, qualifications, and what interns will learn."
                rows={5}
                required
                disabled={isDisabled}
                className={fieldClassName}
              />
            </div>

            <Input
              id="internship-skills"
              label="Skills Required"
              value={skillsInput}
              onChange={(event) => setSkillsInput(event.target.value)}
              placeholder="e.g. React, TypeScript, REST APIs"
              required
              disabled={isDisabled}
            />

            <Input
              id="internship-location"
              label="Location"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="e.g. Bengaluru"
              required
              disabled={isDisabled}
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
                  value={duration}
                  onChange={(event) => setDuration(event.target.value)}
                  placeholder="e.g. 12"
                  required
                  disabled={isDisabled}
                  className={fieldClassName}
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="internship-stipend" className="text-sm font-semibold text-gray-700">
                  Stipend (monthly)
                  <span className="ml-0.5 text-[#da6328]">*</span>
                </label>
                <input
                  id="internship-stipend"
                  type="number"
                  min={0}
                  value={stipend}
                  onChange={(event) => setStipend(event.target.value)}
                  placeholder="e.g. 15000"
                  required
                  disabled={isDisabled}
                  className={fieldClassName}
                />
              </div>
            </div>

            {error && (
              <div className="rounded-md border border-[#ac2b49] bg-white px-3 py-2">
                <p className="text-sm font-medium text-[#ac2b49]">{error}</p>
              </div>
            )}

            {success && (
              <div className="rounded-md border border-[#478356] bg-white px-3 py-2">
                <p className="text-sm font-medium text-[#478356]">{success}</p>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isSubmitting}
              disabled={isDisabled}
            >
              Create Internship
            </Button>
          </form>
        </Card>
      </div>
    </AuthGuard>
  );
}
