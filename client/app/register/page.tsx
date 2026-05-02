'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import RegisterForm from '@/features/auth/RegisterForm';
import { useAuth } from '@/hooks/useAuth';

export default function RegisterPage() {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) return;
    const fallbackPath =
      role === 'admin' ? '/admin' : role === 'company' ? '/company/dashboard' : '/dashboard';
    router.replace(fallbackPath);
  }, [isAuthenticated, role, router]);

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center py-10">
      <div className="w-full max-w-[400px]">
        {/* Compact Header Section */}
        <div className="mb-8 text-center">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
            Government of India
          </span>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#11486b]">Create Account</h1>
          <p className="mt-2 text-xs text-gray-500">
            Join the National Internship Portal to start your journey.
          </p>
        </div>

        {/* The Form is usually wrapped in a Card inside RegisterForm component, 
            if not, wrap <RegisterForm /> in a <Card className="p-6"> */}
        <RegisterForm />

        {/* Action Links Section */}
        <div className="mt-6 space-y-4">
          <div className="rounded border border-gray-200 bg-[#f5f7fa] p-3 text-center">
            <p className="text-[11px] text-gray-500">
              Are you a company?{' '}
              <Link href="/register-company" className="font-bold text-[#11486b] hover:underline">
                Register as Employer
              </Link>
            </p>
          </div>

          <p className="text-center text-xs text-gray-500">
            Already have an account?{' '}
            <Link href="/login" className="font-bold text-[#11486b] hover:underline">
              Sign in here
            </Link>
          </p>
        </div>

        <p className="mt-8 text-center text-[10px] text-gray-500">
          Verified Registration • Digital India Initiative
        </p>
      </div>
    </div>
  );
}
