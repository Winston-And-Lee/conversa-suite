"use client";
import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold mb-8">ConverSA Suite</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <Link 
          href="/assistant" 
          className="p-6 border rounded-lg hover:bg-gray-100 transition-colors"
        >
          <h2 className="text-2xl font-semibold mb-2">Classic Assistant</h2>
          <p className="text-gray-600">
            Use our traditional chat interface to interact with the AI assistant.
          </p>
        </Link>
        <Link 
          href="/assistant-ui" 
          className="p-6 border rounded-lg hover:bg-gray-100 transition-colors"
        >
          <h2 className="text-2xl font-semibold mb-2">Modern Assistant UI</h2>
          <p className="text-gray-600">
            Experience our new assistant-ui powered chat interface with enhanced features.
          </p>
        </Link>
      </div>
    </main>
  );
}
