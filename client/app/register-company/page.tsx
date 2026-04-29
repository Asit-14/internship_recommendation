'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

import RegisterForm from '@/features/auth/RegisterForm';
import { useAuth } from '@/hooks/useAuth';

export default function RegisterCompanyPage() {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) return;
    const fallbackPath =
      role === 'admin' ? '/admin' : role === 'company' ? '/company/dashboard' : '/dashboard';

    router.replace(fallbackPath);
  }, [isAuthenticated, role, router]);

  const handleRegisterSuccess = () => {
    router.replace('/login?registered=1');
  };

  return (
    <div className="flex min-h-[80vh] flex-col items-center justify-center py-10">
      <div className="w-full max-w-[420px]">
        {/* Compact Branding Header */}
        <div className="mb-8 text-center">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
            Government of India
          </span>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#11486b]">
            Employer Registration
          </h1>
          <p className="mx-auto mt-2 max-w-[320px] text-xs text-gray-500 leading-relaxed">
            Create an account to post internships.
            <span className="block font-medium text-gray-500 italic">
              Verification is required before publishing.
            </span>
          </p>
        </div>

        {/* Form Container */}
        <div className="space-y-6">
          <RegisterForm mode="company" onSuccess={handleRegisterSuccess} />

          <div className="text-center">
            <p className="text-xs text-gray-500">
              Looking to apply for internships?{' '}
              <Link href="/register" className="font-bold text-[#11486b] hover:underline">
                Student Registration
              </Link>
            </p>
          </div>
        </div>

        {/* Footer Link */}
        <div className="mt-8 border-t border-gray-200 pt-6 text-center">
          <p className="text-xs text-gray-500">
            Already have an account?{' '}
            <Link href="/login" className="font-bold text-[#11486b] hover:underline">
              Sign in here
            </Link>
          </p>
        </div>

        <p className="mt-8 text-center text-[10px] text-gray-500">
          Official Portal • Ministry of Skill Development
        </p>
      </div>
    </div>
  );
}
