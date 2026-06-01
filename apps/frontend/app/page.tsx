'use client';

import Link from 'next/link';
import { Button } from '@/components/atoms/Button';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-surface to-surface-container flex flex-col items-center justify-center px-6">
      <div className="max-w-2xl text-center space-y-8">
        {/* Logo/Branding */}
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-on-background">
            NeuroHire
          </h1>
          <p className="text-xl text-on-surface-variant">
            AI-Powered Recruitment Platform
          </p>
        </div>

        {/* Tagline */}
        <p className="text-lg text-on-surface-variant leading-relaxed">
          Discover top talent faster with intelligent candidate matching, 
          real-time collaboration, and bias-aware hiring decisions.
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
          <Link href="/auth/login">
            <Button variant="primary" size="lg" className="w-full sm:w-auto">
              Sign In
            </Button>
          </Link>
          <Link href="/auth/register">
            <Button variant="outline" size="lg" className="w-full sm:w-auto">
              Sign Up
            </Button>
          </Link>
        </div>

        {/* Features Preview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
          {[
            {
              icon: '🎯',
              title: 'Smart Matching',
              description: 'AI-powered candidate-job matching with multi-dimensional scoring'
            },
            {
              icon: '⚡',
              title: 'Real-time Collaboration',
              description: 'Live updates and instant notifications for hiring teams'
            },
            {
              icon: '🛡️',
              title: 'Bias Detection',
              description: 'Automated bias detection and DEI score tracking'
            }
          ].map((feature, idx) => (
            <div
              key={idx}
              className="p-6 rounded-lg bg-surface-dim border border-outline-variant hover:border-outline transition-colors"
            >
              <div className="text-4xl mb-3">{feature.icon}</div>
              <h3 className="font-semibold text-on-background mb-2">
                {feature.title}
              </h3>
              <p className="text-sm text-on-surface-variant">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
