import { ThemeDemo } from "@/components/theme-demo";
import { SiteHeader } from "@/components/site-header";

export default function ThemeDemoPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <SiteHeader />
      <main className="flex-1 py-8 md:py-12">
        <ThemeDemo />
      </main>
      <footer className="border-t py-8 md:py-6">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row">
          <p className="text-center text-sm text-muted-foreground md:text-left">
            &copy; {new Date().getFullYear()} Conversa Suite. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
} 