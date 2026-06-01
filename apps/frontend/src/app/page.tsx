'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/atoms/Button';

export default function Home() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-display-lg font-bold text-on-surface mb-4">NeuroHire</h1>
        <p className="text-body-lg text-on-surface-variant mb-8">
          Autonomous Recruitment Intelligence Platform
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/auth/login">
            <Button variant="primary">Sign In</Button>
          </Link>
          <Link href="/auth/register">
            <Button variant="outline">Sign Up</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
