'use client';

import { AxiosError } from 'axios';
import { FormEvent, useState } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import authService from '@/services/auth.service';

type RegisterFormProps = {
  onSuccess?: () => void;
  mode?: 'student' | 'company';
};

export default function RegisterForm({ onSuccess, mode = 'student' }: RegisterFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isCompany = mode === 'company';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (isCompany) {
        await authService.registerCompany({ company_name: name, email, password });
      } else {
        await authService.signup({ name, email, password });
      }
      onSuccess?.();
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : 'Registration failed. Please try again.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <Input
          id="register-name"
          label={isCompany ? 'Company Name' : 'Full Name'}
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder={isCompany ? 'Enter company name' : 'Enter your full name'}
          required
        />

        <Input
          id="register-email"
          label="Email Address"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          required
        />

        <Input
          id="register-password"
          label="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Min 8 chars, uppercase, lowercase, number, special"
          required
        />

        {error && (
          <div className="rounded-md border border-[#ac2b49] bg-white px-3 py-2">
            <p className="text-sm font-medium text-[#ac2b49]">{error}</p>
          </div>
        )}

        <Button type="submit" variant="primary" fullWidth isLoading={isSubmitting}>
          Create Account
        </Button>
      </form>
    </Card>
  );
}
