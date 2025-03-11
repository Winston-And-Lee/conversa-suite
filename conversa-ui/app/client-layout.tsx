'use client';

import { ReactNode } from 'react';
import { FetchMiddlewareProvider } from "@/components/fetch-middleware-provider";
import { ThemeProvider } from "@/lib/theme-provider";
import { ThemeListener } from "@/components/theme-listener";

export function ClientLayout({ children }: { children: ReactNode }) {
  return (
    <FetchMiddlewareProvider>
      <ThemeProvider>
        <ThemeListener />
        {children}
      </ThemeProvider>
    </FetchMiddlewareProvider>
  );
} 