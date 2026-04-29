'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { ChangeEvent, FormEvent, useMemo, useState } from 'react';

import AuthGuard from '@/components/auth/AuthGuard';
import PageHeader from '@/components/layout/PageHeader';
import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input, type SelectOption } from '@/components/ui/Input';
import Spinner from '@/components/ui/Spinner';
import userService, { type UpdateProfilePayload, type UserProfile } from '@/services/user.service';
import { showError, showSuccess } from '@/lib/toast';

type ProfileFormState = {
  name: string;
  email: string;
  phone: string;
  location: string;
  education: string;
  college_name: string;
  branch: string;
  graduation_year: string;
  skills: string[];
};

type EditableField =
  | 'name'
  | 'phone'
  | 'location'
  | 'education'
  | 'college_name'
  | 'branch'
  | 'graduation_year';

type ProfileFormErrors = Partial<Record<EditableField, string>>;

const educationOptions: SelectOption[] = [
  { label: 'Select education level', value: '' },
  { label: '10th', value: '10th' },
  { label: '12th', value: '12th' },
  { label: 'Diploma', value: 'diploma' },
  { label: 'Undergraduate', value: 'undergraduate' },
  { label: 'Postgraduate', value: 'postgraduate' },
  { label: 'PhD', value: 'phd' },
];

const buildGraduationYearOptions = (): SelectOption[] => {
  const currentYear = new Date().getFullYear();
  const options: SelectOption[] = [{ label: 'Select graduation year', value: '' }];

  for (let year = currentYear + 5; year >= currentYear - 15; year -= 1) {
    options.push({ label: String(year), value: String(year) });
  }

  return options;
};

const emptyForm: ProfileFormState = {
  name: '',
  email: '',
  phone: '',
  location: '',
  education: '',
  college_name: '',
  branch: '',
  graduation_year: '',
  skills: [],
};

const toFormState = (profile: UserProfile): ProfileFormState => ({
  name: profile.name ?? '',
  email: profile.email ?? '',
  phone: profile.phone ?? '',
  location: profile.location ?? '',
  education: profile.education ?? '',
  college_name: profile.college_name ?? '',
  branch: profile.branch ?? '',
  graduation_year: profile.graduation_year ? String(profile.graduation_year) : '',
  skills: profile.skills ?? [],
});

const readErrorMessage = (error: unknown, fallback: string): string => {
  if (error instanceof AxiosError) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  return fallback;
};

export default function ProfilePage() {
  const queryClient = useQueryClient();

  const [formDraft, setFormDraft] = useState<ProfileFormState | null>(null);
  const [formErrors, setFormErrors] = useState<ProfileFormErrors>({});
  const [skillInput, setSkillInput] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const graduationYearOptions = useMemo(() => buildGraduationYearOptions(), []);

  const profileQuery = useQuery({
    queryKey: ['user-profile'],
    queryFn: () => userService.getProfile(),
  });

  const activeForm = useMemo<ProfileFormState>(() => {
    if (!profileQuery.data) {
      return emptyForm;
    }

    return formDraft ?? toFormState(profileQuery.data);
  }, [formDraft, profileQuery.data]);

  const updateMutation = useMutation({
    mutationFn: (payload: UpdateProfilePayload) => userService.updateProfile(payload),
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(['user-profile'], updatedProfile);
      setFormDraft(null);
      setFormErrors({});
      showSuccess('Profile updated successfully.');
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to update profile.'));
    },
  });

  const uploadMutation = useMutation({
    mutationFn: (file: File) => userService.uploadResume(file),
    onSuccess: (result) => {
      setResumeFile(null);
      showSuccess(`Resume uploaded successfully: ${result.filename}`);
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to upload resume.'));
    },
  });

  const handleFieldChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profileQuery.data) {
      return;
    }

    const field = event.target.name as EditableField;
    const value = event.target.value;

    setFormDraft((prev) => {
      const base = prev ?? toFormState(profileQuery.data);
      return { ...base, [field]: value };
    });

    setFormErrors((prev) => ({ ...prev, [field]: undefined }));
  };

  const addSkill = () => {
    const normalized = skillInput.trim();
    if (!normalized || !profileQuery.data) {
      return;
    }

    setFormDraft((prev) => {
      const base = prev ?? toFormState(profileQuery.data);
      const exists = base.skills.some((skill) => skill.toLowerCase() === normalized.toLowerCase());
      if (exists) {
        return base;
      }

      return {
        ...base,
        skills: [...base.skills, normalized],
      };
    });

    setSkillInput('');
  };

  const removeSkill = (skillToRemove: string) => {
    if (!profileQuery.data) {
      return;
    }

    setFormDraft((prev) => {
      const base = prev ?? toFormState(profileQuery.data);
      return {
        ...base,
        skills: base.skills.filter((skill) => skill !== skillToRemove),
      };
    });
  };

  const validateForm = (form: ProfileFormState): ProfileFormErrors => {
    const errors: ProfileFormErrors = {};

    if (!form.name.trim()) {
      errors.name = 'Name is required';
    }

    if (!form.location.trim()) {
      errors.location = 'Location is required';
    }

    if (!form.education.trim()) {
      errors.education = 'Education is required';
    }

    if (!form.college_name.trim()) {
      errors.college_name = 'College name is required';
    }

    if (!form.branch.trim()) {
      errors.branch = 'Branch is required';
    }

    if (!form.graduation_year) {
      errors.graduation_year = 'Graduation year is required';
    }

    if (form.phone.trim() && !/^\+?[0-9]{7,15}$/.test(form.phone.trim())) {
      errors.phone = 'Phone must contain 7 to 15 digits and optional leading +';
    }

    return errors;
  };

  const handleProfileSave = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const errors = validateForm(activeForm);
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      showError('Please fix form errors before saving.');
      return;
    }

    const payload: UpdateProfilePayload = {
      name: activeForm.name.trim(),
      phone: activeForm.phone.trim() || null,
      location: activeForm.location.trim(),
      education: activeForm.education.trim(),
      college_name: activeForm.college_name.trim(),
      branch: activeForm.branch.trim(),
      graduation_year: activeForm.graduation_year ? Number(activeForm.graduation_year) : null,
      skills: activeForm.skills,
    };

    updateMutation.mutate(payload);
  };

  const handleResumeUpload = () => {
    if (!resumeFile) {
      showError('Please select a resume file first.');
      return;
    }

    uploadMutation.mutate(resumeFile);
  };

  return (
    <AuthGuard>
      <div className="space-y-8">
        <PageHeader
          title="Profile"
          description="Manage your personal information, skills, and resume."
        />

        {profileQuery.isLoading && (
          <Card>
            <div className="flex items-center gap-2">
              <Spinner label="Loading profile" />
            </div>
          </Card>
        )}

        {profileQuery.isError && (
          <Card>
            <p className="text-sm font-medium text-[#ac2b49]">
              {readErrorMessage(profileQuery.error, 'Failed to load profile.')}
            </p>
            <div className="mt-4">
              <Button variant="primary" onClick={() => profileQuery.refetch()}>
                Retry
              </Button>
            </div>
          </Card>
        )}

        {!profileQuery.isLoading && !profileQuery.isError && profileQuery.data && (
          <form className="space-y-6" onSubmit={handleProfileSave}>
            <Card title="Personal Info">
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  id="name"
                  name="name"
                  label="Name"
                  value={activeForm.name}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.name}
                />
                <Input
                  id="email"
                  name="email"
                  label="Email"
                  type="email"
                  value={activeForm.email}
                  onChange={() => undefined}
                  disabled
                />
                <Input
                  id="phone"
                  name="phone"
                  label="Phone"
                  value={activeForm.phone}
                  onChange={handleFieldChange}
                  placeholder="+91XXXXXXXXXX"
                  error={formErrors.phone}
                />
                <Input
                  id="location"
                  name="location"
                  label="Location"
                  value={activeForm.location}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.location}
                />
              </div>
            </Card>

            <Card title="Education">
              <div className="grid gap-4 sm:grid-cols-2">
                <Input
                  id="education"
                  name="education"
                  label="Education"
                  type="select"
                  options={educationOptions}
                  value={activeForm.education}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.education}
                />
                <Input
                  id="graduation_year"
                  name="graduation_year"
                  label="Graduation Year"
                  type="select"
                  options={graduationYearOptions}
                  value={activeForm.graduation_year}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.graduation_year}
                />
                <Input
                  id="college_name"
                  name="college_name"
                  label="College"
                  value={activeForm.college_name}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.college_name}
                />
                <Input
                  id="branch"
                  name="branch"
                  label="Branch"
                  value={activeForm.branch}
                  onChange={handleFieldChange}
                  required
                  error={formErrors.branch}
                />
              </div>
            </Card>

            <Card title="Skills">
              <div className="grid gap-3 sm:grid-cols-[1fr_auto] sm:items-end">
                <Input
                  id="skill_input"
                  name="skill_input"
                  label="Add Skill"
                  value={skillInput}
                  onChange={(event) => setSkillInput(event.target.value)}
                  placeholder="Type skill and click Add"
                />
                <Button type="button" variant="secondary" onClick={addSkill}>
                  Add
                </Button>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {activeForm.skills.length === 0 && (
                  <p className="text-sm text-gray-500">No skills added yet.</p>
                )}

                {activeForm.skills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600"
                  >
                    {skill}
                    <button
                      type="button"
                      className="text-gray-400 transition-colors hover:text-[#ac2b49]"
                      onClick={() => removeSkill(skill)}
                      aria-label={`Remove ${skill}`}
                    >
                      x
                    </button>
                  </span>
                ))}
              </div>
            </Card>

            <Card title="Resume">
              <div className="space-y-3">
                <Input
                  id="resume"
                  label="Resume file"
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
                />
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-xs text-gray-500">
                    Supported formats: PDF, DOCX. Max size: 5 MB.
                  </p>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleResumeUpload}
                    isLoading={uploadMutation.isPending}
                    disabled={!resumeFile}
                  >
                    Upload Resume
                  </Button>
                </div>
              </div>
            </Card>

            <Card title="Save Changes">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-sm text-gray-500">Review your updates before saving.</p>
                <Button type="submit" variant="primary" isLoading={updateMutation.isPending}>
                  Save Profile
                </Button>
              </div>
            </Card>
          </form>
        )}
      </div>
    </AuthGuard>
  );
}
