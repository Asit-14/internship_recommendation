'use client';

import { useQuery } from '@tanstack/react-query';
import { useParams } from 'next/navigation';
import Link from 'next/link';

import Card from '@/components/ui/Card';
import Spinner from '@/components/ui/Spinner';
import certificateService from '@/services/certificate.service';

export default function CertificateVerificationPage() {
  const { id } = useParams() as { id: string };

  const { data: certificate, isLoading, error } = useQuery({
    queryKey: ['verify-certificate', id],
    queryFn: () => certificateService.verify(id),
    retry: false,
  });

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center py-12 px-4">
      <div className="w-full max-w-2xl text-center mb-8">
        <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-gray-500">
          Government of India
        </span>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-[#11486b]">
          Certificate Verification
        </h1>
        <p className="mt-3 text-sm text-gray-500">
          Verify the authenticity of an internship completion certificate.
        </p>
      </div>

      <Card className="w-full max-w-lg p-8 shadow-xl border-t-4 border-t-[#ffa425]">
        {isLoading ? (
          <div className="py-12 flex flex-col items-center gap-4">
            <Spinner />
            <p className="text-sm text-gray-500">Verifying certificate details...</p>
          </div>
        ) : error ? (
          <div className="py-8 text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-1">Verification Failed</h3>
            <p className="text-sm text-gray-500 mb-6">
              This certificate could not be verified. Please check the ID and try again.
            </p>
            <Link href="/" className="text-sm font-semibold text-[#11486b] hover:underline">
              Return to Home
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="text-center pb-6 border-b border-gray-100">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900">Valid Certificate</h3>
              <p className="text-xs text-[#478356] font-semibold uppercase tracking-wider mt-1">
                Authenticity Verified
              </p>
            </div>

            <div className="grid grid-cols-2 gap-y-4 gap-x-8 text-left">
              <div>
                <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Certificate ID</p>
                <p className="text-sm font-mono font-semibold text-gray-800">{certificate?.certificate_id}</p>
              </div>
              <div>
                <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Issued On</p>
                <p className="text-sm font-semibold text-gray-800">
                  {certificate && new Date(certificate.issued_at).toLocaleDateString(undefined, { dateStyle: 'long' })}
                </p>
              </div>
              <div className="col-span-2 pt-2">
                <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Recipient UID</p>
                <p className="text-sm font-semibold text-gray-800">USR-{certificate?.user_id.toString().padStart(6, '0')}</p>
              </div>
              <div className="col-span-2 pt-2">
                <p className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">Internship Program ID</p>
                <p className="text-sm font-semibold text-gray-800">INT-{certificate?.internship_id.toString().padStart(6, '0')}</p>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-100 text-center">
              <p className="text-[11px] text-gray-400">
                This verification was performed on the official National Internship Portal.
              </p>
            </div>
          </div>
        )}
      </Card>

      <p className="mt-12 text-[10px] text-gray-400 uppercase tracking-widest">
        Secure Verification System • Digital India
      </p>
    </div>
  );
}
