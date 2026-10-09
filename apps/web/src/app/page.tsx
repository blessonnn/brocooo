import { Logo } from "@/components/common/logo";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background selection:bg-lime/30 selection:text-lime">
      <header className="flex items-center justify-between px-8 py-6 max-w-7xl w-full mx-auto">
        <Logo />
        <nav className="flex items-center gap-6 text-sm font-medium">
          <Link href="#features" className="hover:text-lime transition-colors">Features</Link>
          <Link href="#pricing" className="hover:text-lime transition-colors">Pricing (Free)</Link>
          <Link href="/dashboard" className="bg-lime text-background px-5 py-2 rounded-full font-bold hover:bg-lime-light transition-all shadow-[0_0_20px_rgba(198,255,61,0.3)] hover:shadow-[0_0_30px_rgba(198,255,61,0.5)]">
            Open App
          </Link>
        </nav>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 max-w-4xl mx-auto -mt-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface border border-lime/20 text-lime text-sm mb-8">
          <span className="w-2 h-2 rounded-full bg-lime animate-pulse" />
          100% Free & Open Source
        </div>
        
        <h1 className="text-5xl md:text-7xl font-display font-black tracking-tight leading-[1.1] mb-6">
          Turn any video into <br/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-lime to-emerald-400">
            viral shorts.
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-foreground/70 max-w-2xl mb-10">
          Drop a YouTube link or upload a file. Brocooo finds the best hooks, adds trending captions, and gives you ready-to-post clips. No credits. No watermarks.
        </p>
        
        <Link 
          href="/dashboard"
          className="group relative inline-flex items-center justify-center gap-2 bg-lime text-background font-bold text-lg px-8 py-4 rounded-full overflow-hidden transition-all hover:scale-105 shadow-[0_0_30px_rgba(198,255,61,0.4)]"
        >
          <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
          <span className="relative">Start Clipping for Free</span>
          <svg className="relative w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Link>
      </main>
    </div>
  );
}
