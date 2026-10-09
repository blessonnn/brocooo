export default function DashboardPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto">
      <header className="mb-10">
        <h1 className="text-3xl font-display font-bold">Create New Clips</h1>
        <p className="text-foreground/60 mt-2">Paste a link or upload a video to generate shorts.</p>
      </header>

      {/* New Clip Card */}
      <div className="bg-surface border border-white/10 rounded-2xl p-6 shadow-xl mb-12">
        <div className="flex flex-col gap-4">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Paste YouTube link here..." 
              className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-4 text-lg focus:outline-none focus:border-lime/50 focus:ring-1 focus:ring-lime/50 transition-all placeholder:text-foreground/30"
            />
            <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <span className="text-xs text-foreground/40 font-medium px-2">OR</span>
              <button className="bg-white/10 hover:bg-white/20 text-sm font-medium px-4 py-2 rounded-lg transition-colors">
                Upload File
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between mt-2 pt-4 border-t border-white/5">
            <button className="text-sm text-lime hover:text-lime-light transition-colors flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              Advanced Options
            </button>
            <button className="bg-lime text-background font-bold px-8 py-3 rounded-xl hover:bg-lime-light transition-all shadow-[0_0_15px_rgba(198,255,61,0.2)]">
              Get Clips
            </button>
          </div>
        </div>
      </div>

      {/* Explore Section Placeholder */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <svg className="w-5 h-5 text-lime" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            Trending Now
          </h2>
          <span className="text-sm text-foreground/50">Ready to clip</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="group relative aspect-video bg-surface rounded-xl overflow-hidden border border-white/5 cursor-pointer">
              <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors z-10" />
              <div className="absolute bottom-0 left-0 right-0 p-4 z-20 bg-gradient-to-t from-black/90 to-transparent translate-y-2 group-hover:translate-y-0 transition-transform">
                <div className="h-4 w-3/4 bg-white/20 rounded animate-pulse mb-2" />
                <div className="h-3 w-1/2 bg-white/10 rounded animate-pulse" />
              </div>
              <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 z-30 transition-opacity">
                <button className="bg-lime text-background font-bold px-4 py-2 rounded-lg text-sm">
                  Clip This
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
