'use client';

import { AxiosError } from 'axios';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, Suspense, useEffect, useState } from 'react';

import Button from '@/components/ui/Button';
import Card from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import Spinner from '@/components/ui/Spinner';
import { useAuth } from '@/hooks/useAuth';

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[50vh] items-center justify-center">
          <Spinner label="Loading" />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}

const getSafeRedirectPath = (nextPath: string | null): string | null => {
  if (!nextPath) return null;
  if (nextPath.startsWith('/') && !nextPath.startsWith('//') && !nextPath.includes('\\')) {
    return nextPath;
  }
  return null;
};

function LoginContent() {
  const { login, isAuthenticated, role } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nextPath = getSafeRedirectPath(searchParams.get('next'));
  const isFreshRegistration = searchParams.get('registered') === '1';

  useEffect(() => {
    if (!isAuthenticated) return;
    const fallbackPath =
      role === 'admin' ? '/admin' : role === 'company' ? '/company/dashboard' : '/dashboard';
    router.replace(nextPath ?? fallbackPath);
  }, [isAuthenticated, nextPath, role, router]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const { role: loggedRole } = await login({ email, password });
      const fallbackPath =
        loggedRole === 'admin'
          ? '/admin'
          : loggedRole === 'company'
            ? '/company/dashboard'
            : '/dashboard';
      router.replace(nextPath ?? fallbackPath);
    } catch (caughtError: unknown) {
      if (caughtError instanceof AxiosError) {
        const detail = caughtError.response?.data?.detail;
        setError(typeof detail === 'string' ? detail : 'Login failed. Check your credentials.');
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-[70vh] flex-col items-center justify-center py-8">
      <div className="w-full max-w-[380px]">
        {/* Header Section: Tightened meta and title */}
        <div className="mb-8 text-center">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
            Government of India
          </span>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-[#11486b]">Welcome Back</h1>
          <p className="mt-2 text-xs text-gray-500">
            Sign in to your National Internship Portal account.
          </p>
        </div>

        <Card className="p-6">
          {isFreshRegistration && (
            <div className="mb-4 rounded border border-[#478356] bg-white p-2.5 text-center">
              <p className="text-[11px] font-medium text-[#478356]">
                Account created successfully.
              </p>
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
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

            <div className="space-y-1">
              <Input
                id="password"
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="text-sm"
              />
              <div className="flex justify-end">
                <Link
                  href="/forgot-password"
                  title="Coming soon"
                  className="text-[10px] font-medium text-gray-500 hover:text-gray-800"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            {error && (
              <div className="rounded border border-[#ac2b49] bg-white px-3 py-2">
                <p className="text-center text-[11px] font-medium text-[#ac2b49]">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isSubmitting}
              className="h-10 text-xs font-semibold"
            >
              Sign In
            </Button>
          </form>

          <div className="mt-6 border-t border-gray-200 pt-4 text-center">
            <p className="text-xs text-gray-500">
              New to the portal?{' '}
              <Link href="/register" className="font-bold text-[#11486b] hover:underline">
                Register here
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
