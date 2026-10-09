import Link from "next/link";
import React from "react";

export function Logo({ className = "" }: { className?: string }) {
  return (
    <Link href="/" className={`flex items-center gap-2 ${className}`}>
      <div className="bg-lime text-background font-display font-black text-xl italic px-3 py-1 rounded-full shadow-[0_0_15px_rgba(198,255,61,0.5)] tracking-tighter">
        brocooo
      </div>
    </Link>
  );
}
