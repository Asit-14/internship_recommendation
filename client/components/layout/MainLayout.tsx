import { ReactNode } from 'react';

import Footer from '@/components/layout/Footer';
import Navbar from '@/components/layout/Navbar';
import PageContainer from '@/components/layout/PageContainer';

type MainLayoutProps = {
  children: ReactNode;
};

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7fa] text-gray-800">
      <Navbar />
      <main className="flex-1 py-8" suppressHydrationWarning>
        <PageContainer>{children}</PageContainer>
      </main>
      <Footer />
    </div>
  );
}
