import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Recruiter — Resume Analysis & Mock Interviews",
  description:
    "AI-powered resume parsing, candidate scoring, and mock interview simulation",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-4xl mx-auto px-4 py-3 flex gap-6">
            <Link href="/" className="text-gray-900 font-medium hover:text-blue-600">
              Resume Analyzer
            </Link>
            <Link href="/interview" className="text-gray-600 hover:text-blue-600">
              Mock Interview
            </Link>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
