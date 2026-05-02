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
import Modal from '@/components/ui/Modal';
import { removeToken } from '@/lib/axios';
import { useRouter } from 'next/navigation';

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
  company_description: string;
  website: string;
  industry: string;
  company_size: string;
  established_year: string;
};

type EditableField =
  | 'name'
  | 'phone'
  | 'location'
  | 'education'
  | 'college_name'
  | 'branch'
  | 'graduation_year'
  | 'company_description'
  | 'website'
  | 'industry'
  | 'company_size'
  | 'established_year';

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

const buildEstablishedYearOptions = (): SelectOption[] => {
  const currentYear = new Date().getFullYear();
  const options: SelectOption[] = [{ label: 'Select established year', value: '' }];

  for (let year = currentYear; year >= 1800; year -= 1) {
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
  company_description: '',
  website: '',
  industry: '',
  company_size: '',
  established_year: '',
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
  company_description: profile.company_description ?? '',
  website: profile.website ?? '',
  industry: profile.industry ?? '',
  company_size: profile.company_size ?? '',
  established_year: profile.established_year ? String(profile.established_year) : '',
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
  const router = useRouter();

  const [formDraft, setFormDraft] = useState<ProfileFormState | null>(null);
  const [formErrors, setFormErrors] = useState<ProfileFormErrors>({});
  const [skillInput, setSkillInput] = useState('');
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleteConfirmation, setDeleteConfirmation] = useState('');

  const graduationYearOptions = useMemo(() => buildGraduationYearOptions(), []);
  const establishedYearOptions = useMemo(() => buildEstablishedYearOptions(), []);

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
      showSuccess(`Resume uploaded successfully.`);
      queryClient.invalidateQueries({ queryKey: ['user-profile'] });
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to upload resume.'));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => userService.deleteAccount(deletePassword, deleteConfirmation),
    onSuccess: () => {
      showSuccess('Your account has been deleted.');
      removeToken();
      router.push('/login');
    },
    onError: (error) => {
      showError(readErrorMessage(error, 'Failed to delete account. Please check your password.'));
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
    const role = profileQuery.data?.role;

    if (!form.name.trim()) {
      errors.name = role === 'company' ? 'Company name is required' : 'Name is required';
    }

    if (!form.location.trim()) {
      errors.location = 'Location is required';
    }

    if (form.phone.trim() && !/^\+?[0-9]{7,15}$/.test(form.phone.trim())) {
      errors.phone = 'Phone must contain 7 to 15 digits and optional leading +';
    }

    if (role === 'company') {
      if (!form.company_description.trim()) {
        errors.company_description = 'Company description is required';
      }
      if (!form.industry.trim()) {
        errors.industry = 'Industry is required';
      }
      if (!form.established_year) {
        errors.established_year = 'Established year is required';
      }
    } else {
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

    const isCompany = profileQuery.data?.role === 'company';

    const payload: UpdateProfilePayload = {
      name: activeForm.name.trim(),
      phone: activeForm.phone.trim() || null,
      location: activeForm.location.trim(),
      
      education: isCompany ? null : activeForm.education.trim(),
      college_name: isCompany ? null : activeForm.college_name.trim(),
      branch: isCompany ? null : activeForm.branch.trim(),
      graduation_year: (!isCompany && activeForm.graduation_year) ? Number(activeForm.graduation_year) : null,
      skills: isCompany ? [] : activeForm.skills,
      
      company_description: isCompany ? activeForm.company_description.trim() : null,
      website: isCompany ? (activeForm.website.trim() || null) : null,
      industry: isCompany ? activeForm.industry.trim() : null,
      company_size: isCompany ? (activeForm.company_size.trim() || null) : null,
      established_year: (isCompany && activeForm.established_year) ? Number(activeForm.established_year) : null,
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

            {profileQuery.data.role === 'company' && (
              <Card title="Company Details">
                <div className="grid gap-4 sm:grid-cols-2">
                  <Input
                    id="company_description"
                    name="company_description"
                    label="Description"
                    value={activeForm.company_description}
                    onChange={handleFieldChange}
                    required
                    error={formErrors.company_description}
                  />
                  <Input
                    id="industry"
                    name="industry"
                    label="Industry"
                    value={activeForm.industry}
                    onChange={handleFieldChange}
                    required
                    error={formErrors.industry}
                  />
                  <Input
                    id="company_size"
                    name="company_size"
                    label="Company Size (e.g. 1-10, 50-100)"
                    value={activeForm.company_size}
                    onChange={handleFieldChange}
                    error={formErrors.company_size}
                  />
                  <Input
                    id="established_year"
                    name="established_year"
                    label="Established Year"
                    type="select"
                    options={establishedYearOptions}
                    value={activeForm.established_year}
                    onChange={handleFieldChange}
                    required
                    error={formErrors.established_year}
                  />
                  <Input
                    id="website"
                    name="website"
                    label="Website URL"
                    type="url"
                    value={activeForm.website}
                    onChange={handleFieldChange}
                    error={formErrors.website}
                  />
                </div>
              </Card>
            )}

            {profileQuery.data.role !== 'company' && (
              <>
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
                  onChange={(event) => {
                    const target = event.target as HTMLInputElement;
                    setResumeFile(target.files?.[0] ?? null);
                  }}
                />
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex flex-col gap-1">
                    <p className="text-xs text-gray-500">
                      Supported formats: PDF, DOCX. Max size: 5 MB.
                    </p>
                    {profileQuery.data?.resume_url && (
                      <a 
                        href={profileQuery.data.resume_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                        View current resume
                      </a>
                    )}
                  </div>
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
              </>
            )}

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

        <div className="pt-8 border-t border-gray-200">
          <Card 
            title="Danger Zone" 
            className="border-red-100 bg-red-50/30"
          >
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h4 className="text-sm font-semibold text-red-800">Delete Account</h4>
                <p className="text-sm text-red-600 mt-1">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
              </div>
              <Button 
                variant="secondary" 
                className="bg-white text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
                onClick={() => setIsDeleteModalOpen(true)}
              >
                Delete Account
              </Button>
            </div>
          </Card>
        </div>

        <Modal
          isOpen={isDeleteModalOpen}
          onClose={() => {
            setIsDeleteModalOpen(false);
            setDeletePassword('');
            setDeleteConfirmation('');
          }}
          title="Confirm Account Deletion"
          variant="danger"
          footer={
            <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end w-full">
              <Button 
                variant="secondary" 
                onClick={() => {
                  setIsDeleteModalOpen(false);
                  setDeletePassword('');
                  setDeleteConfirmation('');
                }}
              >
                Cancel
              </Button>
              <Button 
                variant="primary" 
                className="bg-red-600 hover:bg-red-700 border-red-600"
                onClick={() => deleteMutation.mutate()}
                isLoading={deleteMutation.isPending}
                disabled={deleteConfirmation !== 'DELETE' || !deletePassword}
              >
                Permanently Delete
              </Button>
            </div>
          }
        >
          <div className="space-y-4">
            <div className="rounded-lg bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Warning</h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>
                      This action is permanent and cannot be undone. All your data including applications, 
                      internships, and certificates will be deactivated or removed.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <Input
                id="delete-password"
                label="Confirm Password"
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Enter your current password"
                required
              />
              <Input
                id="delete-confirmation"
                label={
                  <span>
                    Type <span className="font-bold">DELETE</span> to confirm
                  </span>
                }
                value={deleteConfirmation}
                onChange={(e) => setDeleteConfirmation(e.target.value)}
                placeholder="DELETE"
                required
              />
            </div>
          </div>
        </Modal>
      </div>
    </AuthGuard>
  );
}
