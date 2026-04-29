'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

import Button from '@/components/ui/Button';
import { useAuth } from '@/hooks/useAuth';

const publicLinks = [{ label: 'Home', href: '/' }];

export default function Navbar() {
  const pathname = usePathname();
  const { isAuthenticated, logout, role } = useAuth();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const isLoggedIn = isAuthenticated;

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsMounted(true);
    }, 0);
    return () => clearTimeout(timer);
  }, []);

  const navLinks = (() => {
    if (!isMounted || !isLoggedIn) return publicLinks;
    if (role === 'student') {
      return [
        { label: 'Dashboard', href: '/dashboard' },
        { label: 'Applications', href: '/applications' },
        { label: 'Profile', href: '/profile' },
      ];
    }
    if (role === 'company') {
      return [
        { label: 'Dashboard', href: '/company/dashboard' },
        { label: 'Internships', href: '/company/internships' },
        { label: 'Create Internship', href: '/company/create-internship' },
        { label: 'Profile', href: '/profile' },
      ];
    }
    if (role === 'admin') {
      return [
        { label: 'Admin Panel', href: '/admin' },
        { label: 'Analytics', href: '/admin/analytics' },
      ];
    }
    return publicLinks;
  })();

  return (
    <header className="sticky top-0 z-40">
      <div className="bg-[#11486b] text-white">
        <div className="mx-auto flex h-14 w-full max-w-7xl items-center justify-between px-4">
          <div className="flex flex-col leading-tight">
            <span className="text-[11px] uppercase tracking-[0.25em] text-white/70">
              Government of India
            </span>
            <span className="text-sm font-semibold">National Internship Portal</span>
          </div>
          <span className="hidden text-xs font-semibold text-white/80 sm:inline">
            Official Internship Services
          </span>
        </div>
      </div>

      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto flex h-14 w-full max-w-7xl items-center justify-between px-4">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-sm font-semibold text-[#11486b]">
              NIP
            </Link>

            <nav className="hidden items-center gap-6 md:flex">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`inline-flex h-14 items-center border-b-2 px-1 text-sm font-medium transition-colors ${
                    pathname === link.href
                      ? 'border-[#ffa425] text-gray-800'
                      : 'border-transparent text-gray-500 hover:text-gray-800'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {isMounted && isLoggedIn ? (
              <Button
                variant="secondary"
                onClick={logout}
                className="hidden h-9 px-4 text-xs font-semibold sm:inline-flex"
              >
                Logout
              </Button>
            ) : (
              <Link href="/login" className="hidden sm:block">
                <Button variant="primary" className="h-9 px-4 text-xs font-semibold">
                  Sign In
                </Button>
              </Link>
            )}

            <button
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center rounded-md text-gray-600 transition hover:bg-gray-100 md:hidden"
              onClick={() => setIsMobileOpen((o) => !o)}
              aria-label="Toggle navigation"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                {isMobileOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {isMobileOpen && (
        <nav className="border-b border-gray-200 bg-white p-4 md:hidden">
          <div className="flex flex-col gap-3">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMobileOpen(false)}
                className={`border-l-2 pl-3 text-sm font-medium ${
                  pathname === link.href
                    ? 'border-[#ffa425] text-gray-800'
                    : 'border-transparent text-gray-500'
                }`}
              >
                {link.label}
              </Link>
            ))}
            <div className="border-t border-gray-200 pt-3">
              {isMounted && isLoggedIn ? (
                <button onClick={logout} className="text-left text-sm font-medium text-gray-600">
                  Logout
                </button>
              ) : (
                <Link
                  href="/login"
                  onClick={() => setIsMobileOpen(false)}
                  className="text-sm font-medium text-gray-600"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}
