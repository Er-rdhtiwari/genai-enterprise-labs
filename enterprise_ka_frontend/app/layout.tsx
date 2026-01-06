import "./globals.css";
import type { ReactNode } from "react";
import { Space_Grotesk } from "next/font/google";
import Link from "next/link";

const grotesk = Space_Grotesk({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export const metadata = {
  title: "Enterprise Knowledge Assistant UI",
  description: "Frontend to exercise the Enterprise KA FastAPI backend",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={grotesk.className}>
        <header className="app-header">
          <div className="brand">
            <span className="dot" />
            <div>
              <div className="title">Enterprise Knowledge Assistant</div>
              <div className="subtitle">RAG + Prompt Safety</div>
            </div>
          </div>
          <nav>
            <Link href="https://github.com/Er-rdhtiwari/genai-enterprise-labs" target="_blank">
              Repo
            </Link>
          </nav>
        </header>
        <main className="app-shell">{children}</main>
        <footer className="app-footer">
          <span>Backend: FastAPI (enterprise_ka)</span>
          <span>Frontend: Next.js 14 (app router)</span>
        </footer>
      </body>
    </html>
  );
}
