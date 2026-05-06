import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { StoreHydration } from "@/components/StoreHydration";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Emora - AI Emotional Companion",
  description: "Your digital sanctuary for emotional wellness and journaling.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} font-sans antialiased bg-background text-foreground min-h-screen relative overflow-x-hidden`}>

        {/* ── Rich ambient background ── */}
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          {/* Base deep navy */}
          <div className="absolute inset-0 bg-[#080e1d]" />
          {/* Radial centre glow */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(100,60,220,0.22),transparent)]" />
          {/* Top-left violet orb */}
          <div className="absolute -top-[15%] -left-[10%] w-[55vw] h-[55vw] rounded-full bg-[#5b21b6]/25 blur-[120px] bg-glow-pulse" />
          {/* Bottom-right cyan orb */}
          <div className="absolute -bottom-[15%] -right-[10%] w-[50vw] h-[50vw] rounded-full bg-[#0891b2]/15 blur-[130px] bg-glow-pulse-slow" style={{ animationDelay: "2.5s" }} />
          {/* Mid rose accent */}
          <div className="absolute top-[40%] left-[55%] w-[30vw] h-[30vw] rounded-full bg-[#be185d]/10 blur-[90px] bg-glow-pulse" style={{ animationDelay: "4s" }} />
          {/* Subtle grid overlay */}
          <div
            className="absolute inset-0 opacity-[0.025]"
            style={{ backgroundImage: "linear-gradient(rgba(255,255,255,0.4) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.4) 1px,transparent 1px)", backgroundSize: "80px 80px" }}
          />
        </div>

        <StoreHydration />
        {children}
      </body>
    </html>
  );
}
