'use client';

import { AxiosError } from 'axios';
import { FormEvent, useState } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import authService from '@/services/auth.service';
import { showError, showSuccess } from '@/lib/toast';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';

type RegisterFormProps = {
  onSuccess?: () => void;
  mode?: 'student' | 'company';
};

export default function RegisterForm({ onSuccess, mode = 'student' }: RegisterFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  
  const isCompany = mode === 'company';
  const { loginWithOTP } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (!otpSent) {
        if (isCompany) {
          await authService.registerCompany({ company_name: name, email, password });
        } else {
          await authService.signup({ name, email, password });
        }
        await authService.sendOTP({ email });
        setOtpSent(true);
        showSuccess('OTP sent to your email. Please verify to continue.');
      } else {
        const { role } = await loginWithOTP({ email, otp });
        showSuccess('Registration and login successful');
        
        if (onSuccess) {
          onSuccess();
        } else {
          const fallbackPath =
            role === 'admin' ? '/admin' : role === 'company' ? '/company/dashboard' : '/dashboard';
          router.replace(fallbackPath);
        }
      }
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        const detail = err.response?.data?.detail;
        showError(typeof detail === 'string' ? detail : 'An error occurred. Please try again.');
      } else {
        showError('An error occurred. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <form className="space-y-4" onSubmit={handleSubmit}>
        {!otpSent ? (
          <>
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
          </>
        ) : (
          <Input
            id="register-otp"
            label="Enter OTP"
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="6-digit OTP"
            required
            maxLength={6}
          />
        )}

        <Button type="submit" variant="primary" fullWidth isLoading={isSubmitting}>
          {otpSent ? 'Verify & Login' : 'Create Account'}
        </Button>
      </form>
    </Card>
  );
}
