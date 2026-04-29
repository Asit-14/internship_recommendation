import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';

import MainLayout from '@/components/layout/MainLayout';
import Providers from '@/components/layout/Providers';

import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'National Internship Portal — Government of India',
  description:
    'Discover verified government and private sector internship opportunities. Get AI-powered recommendations, track applications, and build your career with the National Internship Portal.',
  keywords: ['internship', 'government', 'India', 'career', 'student', 'recommendation'],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      data-scroll-behavior="smooth"
    >
      <body className="min-h-full bg-[#f5f7fa] font-sans text-gray-800">
        <Providers>
          <MainLayout>{children}</MainLayout>
        </Providers>
      </body>
    </html>
  );
}
