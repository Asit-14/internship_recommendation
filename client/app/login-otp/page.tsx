'use client';

import { AxiosError } from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { useAuth } from '@/hooks/useAuth';
import authService from '@/services/auth.service';
import { showError, showSuccess } from '@/lib/toast';

export default function LoginOTPPage() {
  const router = useRouter();
  const { loginWithOTP } = useAuth();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSendOTP = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await authService.sendOTP({ email });
      showSuccess('OTP sent successfully to your email');
      setStep('otp');
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        showError(err.response?.data?.detail || 'Failed to send OTP');
      } else {
        showError('Something went wrong');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const { role: loggedRole } = await loginWithOTP({ email, otp });
      showSuccess('Logged in successfully');
      
      const fallbackPath =
        loggedRole === 'admin'
          ? '/admin'
          : loggedRole === 'company'
            ? '/company/dashboard'
            : '/dashboard';
      
      router.replace(fallbackPath);
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        showError(err.response?.data?.detail || 'Invalid OTP');
      } else {
        showError('Something went wrong');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center py-8">
      <div className="w-full max-w-[380px]">
        <div className="mb-8 text-center">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
            Government of India
          </span>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#11486b]">
            {step === 'email' ? 'Login with OTP' : 'Verify OTP'}
          </h1>
          <p className="mt-2 text-xs text-gray-500">
            {step === 'email'
              ? 'Enter your email to receive a 6-digit login code.'
              : `Enter the 6-digit code sent to ${email}.`}
          </p>
        </div>

        <Card className="p-6">
          {step === 'email' && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <Input
                id="email"
                label="Email Address"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@mail.gov.in"
                required
                className="text-sm"
              />
              <Button
                type="submit"
                variant="primary"
                fullWidth
                isLoading={isSubmitting}
                className="h-10 text-xs font-semibold"
              >
                Send OTP
              </Button>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleLogin} className="space-y-4">
              <Input
                id="otp"
                label="6-Digit OTP"
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                required
                maxLength={6}
                className="text-sm text-center tracking-[0.5em] font-bold"
              />
              <Button
                type="submit"
                variant="primary"
                fullWidth
                isLoading={isSubmitting}
                className="h-10 text-xs font-semibold"
              >
                Login
              </Button>
              <button
                type="button"
                onClick={() => setStep('email')}
                className="w-full text-center text-xs text-gray-500 hover:text-gray-800"
              >
                Change Email
              </button>
            </form>
          )}

          <div className="mt-6 border-t border-gray-200 pt-4 text-center">
            <p className="text-xs text-gray-500">
              Back to{' '}
              <Link href="/login" className="font-bold text-[#11486b] hover:underline">
                Password Login
              </Link>
            </p>
          </div>
        </Card>

        <p className="mt-6 text-center text-[10px] text-gray-500">
          Secure Login • Digital India Mission
        </p>
      </div>
    </div>
  );
}
