'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useMemo } from 'react';

import { type AuthRole, useAuth } from '@/hooks/useAuth';

type AuthGuardProps = {
  children: React.ReactNode;
  allowedRoles?: AuthRole[];
  redirectTo?: string;
  unauthorizedRedirectTo?: string;
  fallback?: React.ReactNode;
};

type GuardStatus = 'unauthenticated' | 'unauthorized' | 'authorized';

export default function AuthGuard({
  children,
  allowedRoles,
  redirectTo = '/login',
  unauthorizedRedirectTo = '/dashboard',
  fallback,
}: AuthGuardProps) {
  const { isAuthenticated, role } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const guardStatus = useMemo<GuardStatus>(() => {
    const hasSession = isAuthenticated;
    if (!hasSession) {
      return 'unauthenticated';
    }

    if (allowedRoles && allowedRoles.length > 0) {
      if (!role || !allowedRoles.includes(role)) {
        return 'unauthorized';
      }
    }

    return 'authorized';
  }, [allowedRoles, isAuthenticated, role]);

  useEffect(() => {
    if (guardStatus === 'unauthenticated') {
      const loginPath = `${redirectTo}?next=${encodeURIComponent(pathname || '/')}`;
      router.replace(loginPath);
      return;
    }

    if (guardStatus === 'unauthorized') {
      router.replace(unauthorizedRedirectTo);
    }
  }, [guardStatus, pathname, redirectTo, router, unauthorizedRedirectTo]);

  if (guardStatus !== 'authorized') {
    return (
      fallback ?? (
        <div className="flex min-h-screen items-center justify-center bg-[#f5f7fa] text-gray-800">
          Checking authentication...
        </div>
      )
    );
  }

  return <>{children}</>;
}
