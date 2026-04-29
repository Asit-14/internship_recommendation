'use client';

import { AxiosError } from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import authService from '@/services/auth.service';
import { showError, showSuccess } from '@/lib/toast';

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [step, setStep] = useState<'email' | 'otp' | 'reset'>('email');
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

  const handleVerifyOTP = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await authService.verifyOTP({ email, otp });
      showSuccess('OTP verified successfully');
      setStep('reset');
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

  const handleResetPassword = async (e: FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      showError('Passwords do not match');
      return;
    }
    setIsSubmitting(true);
    try {
      await authService.resetPassword({ email, otp, new_password: newPassword });
      showSuccess('Password reset successfully. You can now login.');
      router.push('/login');
    } catch (err: unknown) {
      if (err instanceof AxiosError) {
        showError(err.response?.data?.detail || 'Failed to reset password');
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
            {step === 'email' ? 'Forgot Password' : step === 'otp' ? 'Verify OTP' : 'Reset Password'}
          </h1>
          <p className="mt-2 text-xs text-gray-500">
            {step === 'email'
              ? 'Enter your email to receive a 6-digit OTP code.'
              : step === 'otp'
                ? `Enter the 6-digit code sent to ${email}.`
                : 'Enter your new password below.'}
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
            <form onSubmit={handleVerifyOTP} className="space-y-4">
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
                Verify OTP
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

          {step === 'reset' && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <Input
                id="new-password"
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="text-sm"
              />
              <Input
                id="confirm-password"
                label="Confirm New Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
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
                Reset Password
              </Button>
            </form>
          )}

          <div className="mt-6 border-t border-gray-200 pt-4 text-center">
            <p className="text-xs text-gray-500">
              Remembered your password?{' '}
              <Link href="/login" className="font-bold text-[#11486b] hover:underline">
                Sign In
              </Link>
            </p>
          </div>
        </Card>

        <p className="mt-6 text-center text-[10px] text-gray-500">
          Secure Reset • Digital India Mission
        </p>
      </div>
    </div>
  );
}
