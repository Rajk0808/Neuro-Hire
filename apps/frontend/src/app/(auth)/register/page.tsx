'use client';

import React from 'react';
import { Button } from '@/components/atoms/Button';
import Link from 'next/link';

export default function RegisterPage() {
  const [formData, setFormData] = React.useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-md">
        <h1 className="text-headline-lg font-bold text-on-surface mb-2">Create Account</h1>
        <p className="text-on-surface-variant mb-8">Join NeuroHire to start hiring smarter</p>

        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Password
            </label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => handleChange('password', e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-on-surface-variant mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => handleChange('confirmPassword', e.target.value)}
              className="w-full px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
            />
          </div>

          <Button variant="primary" className="w-full">
            Create Account
          </Button>
        </form>

        <p className="text-center text-on-surface-variant mt-6">
          Already have an account?{' '}
          <Link href="/auth/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
