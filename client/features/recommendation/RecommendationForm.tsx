'use client';

import { ChangeEvent, FormEvent, useState } from 'react';

import Button from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ACCEPTED_TYPES = new Set([
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]);

export type RecommendationFormData = {
  file: File;
};

type RecommendationFormProps = {
  onSubmit: (data: RecommendationFormData) => void;
  isLoading?: boolean;
};

export default function RecommendationForm({
  onSubmit,
  isLoading = false,
}: RecommendationFormProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0] ?? null;

    if (!file) {
      setSelectedFile(null);
      setError('Please upload a resume in PDF or DOCX format.');
      return;
    }

    const extension = file.name.split('.').pop()?.toLowerCase();
    const hasValidExtension = extension === 'pdf' || extension === 'docx';
    const hasValidType = file.type ? ACCEPTED_TYPES.has(file.type) : hasValidExtension;

    if (!hasValidType || !hasValidExtension) {
      setSelectedFile(null);
      setError('Unsupported file type. Please upload a PDF or DOCX resume.');
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setSelectedFile(null);
      setError('File size exceeds 5 MB. Please upload a smaller resume.');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    if (!selectedFile) {
      setError('Please upload a resume to continue.');
      return;
    }

    onSubmit({ file: selectedFile });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div className="space-y-1">
        <h3 className="text-lg font-semibold text-[#11486b]">Analyze your resume</h3>
        <p className="text-sm text-gray-500">
          Upload a resume to extract skills and get internship recommendations instantly.
        </p>
      </div>

      <div className="space-y-3">
        <Input
          id="resume"
          label="Resume file"
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleFileChange}
          disabled={isLoading}
        />
        <p className="text-xs text-gray-500">Accepted formats: PDF, DOCX (max 5 MB).</p>
        {selectedFile && !error && (
          <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-600">
            {selectedFile.name} · {(selectedFile.size / 1024).toFixed(0)} KB
          </div>
        )}
        {error && <p className="text-xs font-medium text-[#ac2b49]">{error}</p>}
      </div>

      <Button
        type="submit"
        variant="primary"
        fullWidth
        isLoading={isLoading}
        disabled={!selectedFile || !!error}
        className="mt-2 py-3 text-base"
      >
        Analyze Resume
      </Button>
    </form>
  );
}
