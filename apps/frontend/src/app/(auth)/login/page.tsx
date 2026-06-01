'use client';

import React from 'react';
import { Button } from '@/components/atoms/Button';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-md">
        <h1 className="text-headline-lg font-bold text-on-surface mb-2">Sign In</h1>
        <p className="text-on-surface-variant mb-8">Welcome back to NeuroHire</p>

        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <Button variant="primary" className="w-full">
            Sign In
          </Button>
        </form>

        <p className="text-center text-on-surface-variant mt-6">
          Don't have an account?{' '}
          <Link href="/auth/register" className="text-primary hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
