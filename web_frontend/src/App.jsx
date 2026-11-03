import React, { useState } from 'react';
import Auth from './Auth.jsx';
import { 
  Sparkles, 
  Search, 
  Youtube, 
  Compass, 
  Layers, 
  Zap, 
  ExternalLink, 
  CheckCircle2, 
  Clock, 
  Eye, 
  ChevronRight, 
  ArrowRight,
  ShieldCheck,
  MousePointerClick,
  Filter,
  Flame,
  Award
} from 'lucide-react';

const SAMPLES = [
  {
    id: 'crochet',
    title: 'Crochet Tortoise Keychain',
    category: 'Amigurumi Crochet',
    materials: 'Yarn, Polyester Fiberfill, Keyring',
    imageUrl: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80',
    query: 'how to crochet turtle keychain amigurumi tutorial',
    results: [
      {
        title: 'Super Easy Crochet Turtle Keychain for Beginners (Step-by-Step)',
        channel: 'Club Crochet',
        views: '1.4M views',
        duration: '18m, 42s',
        score: '0.94',
        match: '98% match',
        thumbnail: 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=600&q=80'
      },
      {
        title: 'Mini Sea Turtle Amigurumi • Fast 15-Minute Pattern Walkthrough',
        channel: 'All About Ami',
        views: '840k views',
        duration: '14m, 10s',
        score: '0.89',
        match: '94% match',
        thumbnail: 'https://images.unsplash.com/photo-1607344645866-009c320c5ab8?auto=format&fit=crop&w=600&q=80'
      },
      {
        title: 'How to Attach Keyrings to Crochet Plushies Neatly',
        channel: 'Crafty Hands Studio',
        views: '320k views',
        duration: '07m, 55s',
        score: '0.82',
        match: '88% match',
        thumbnail: 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=600&q=80'
      }
    ]
  },
  {
    id: 'origami',
    title: 'Kusudama Flower Ball',
    category: 'Papercraft / Origami',
    materials: 'Origami Paper, Craft Glue, Ribbon',
    imageUrl: 'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?auto=format&fit=crop&w=800&q=80',
    query: 'origami kusudama flower ball tutorial step by step',
    results: [
      {
        title: 'Modular Origami Kusudama Flower Ball (Full Beginner Tutorial)',
        channel: 'Paper Kawaii',
        views: '2.1M views',
        duration: '22m, 15s',
        score: '0.96',
        match: '99% match',
        thumbnail: 'https://images.unsplash.com/photo-1518895949257-7621c3c786d7?auto=format&fit=crop&w=600&q=80'
      },
      {
        title: 'How to Fold 5-Petal Origami Flowers for Kusudama',
        channel: 'Origami Princess',
        views: '920k views',
        duration: '11m, 30s',
        score: '0.88',
        match: '92% match',
        thumbnail: 'https://images.unsplash.com/photo-1530982011887-3ce11ab80496?auto=format&fit=crop&w=600&q=80'
      }
    ]
  },
  {
    id: 'woodworking',
    title: 'Carved Walnut Cooking Spoon',
    category: 'Spoon Carving',
    materials: 'Black Walnut Wood, Mineral Oil, Hook Knife',
    imageUrl: 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=800&q=80',
    query: 'how to carve wooden cooking spoon with hand tools tutorial',
    results: [
      {
        title: 'Spoon Carving for Absolute Beginners with Only 2 Hand Tools',
        channel: 'Wood & Whittle',
        views: '760k views',
        duration: '26m, 10s',
        score: '0.93',
        match: '97% match',
        thumbnail: 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?auto=format&fit=crop&w=600&q=80'
      },
      {
        title: 'Finishing and Food-Safe Oil Treatment for Hand-Carved Utensils',
        channel: 'Traditional Craft Hub',
        views: '410k views',
        duration: '09m, 45s',
        score: '0.85',
        match: '90% match',
        thumbnail: 'https://images.unsplash.com/photo-1513519245088-0e12902e5a38?auto=format&fit=crop&w=600&q=80'
      }
    ]
  }
];

export default function App() {
  const [currentView, setCurrentView] = useState('landing'); // 'landing' | 'auth'
  const [authInitialMode, setAuthInitialMode] = useState('login'); // 'login' | 'signup'
  const [selectedSample, setSelectedSample] = useState(SAMPLES[0]);
  const [activeTab, setActiveTab] = useState('features');

  if (currentView === 'auth') {
    return (
      <Auth 
        initialMode={authInitialMode} 
        onBackToHome={() => setCurrentView('landing')} 
      />
    );
  }

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-stone-900 font-sans selection:bg-amber-200">
      
      {/* Ambient background decoration */}
      <div className="fixed inset-0 pointer-events-none bg-grid-pattern opacity-40 z-0"></div>
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] glow-ambient pointer-events-none z-0"></div>

      {/* Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-stone-200/70 bg-[#FAF8F5]/85 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 cursor-pointer">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-amber-600 to-amber-400 flex items-center justify-center text-white shadow-md shadow-amber-500/20">
              <span className="text-xl">🧶</span>
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-stone-900 flex items-center gap-1.5">
                Link Hunter
                <span className="text-[10px] font-semibold uppercase tracking-wider bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full border border-amber-200">
                  AI Beta
                </span>
              </span>
              <p className="text-[11px] font-medium text-stone-500 tracking-wide">Reverse Craft Search</p>
            </div>
          </div>

          {/* Desktop Nav Links */}
          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-stone-600">
            <a href="#how-it-works" className="hover:text-amber-800 transition-colors">How it Works</a>
            <a href="#interactive-demo" className="hover:text-amber-800 transition-colors">Interactive Demo</a>
            <a href="#pipeline" className="hover:text-amber-800 transition-colors">AI Pipeline</a>
            <a href="#faq" className="hover:text-amber-800 transition-colors">FAQ</a>
          </nav>

          {/* Action CTAs */}
          <div className="flex items-center space-x-4">
            <button 
              onClick={() => {
                setAuthInitialMode('login');
                setCurrentView('auth');
              }}
              className="hidden sm:inline-flex text-sm font-semibold text-stone-700 hover:text-stone-950 px-4 py-2 transition-colors cursor-pointer"
            >
              Sign In
            </button>
            <button
              onClick={() => {
                setAuthInitialMode('signup');
                setCurrentView('auth');
              }}
              className="hidden md:inline-flex text-sm font-semibold text-amber-800 bg-amber-50 hover:bg-amber-100 border border-amber-200/80 px-4 py-2 rounded-full transition-colors cursor-pointer"
            >
              Sign Up
            </button>
            <a 
              href="https://github.com/debjitghorai/LH" 
              target="_blank" 
              rel="noreferrer"
              className="inline-flex items-center space-x-2 text-sm font-semibold text-white bg-stone-900 hover:bg-stone-800 px-5 py-2.5 rounded-full shadow-sm hover:shadow-md transition-all active:scale-[0.98]"
            >
              <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>Add to Chrome</span>
            </a>
          </div>

        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 pt-16 pb-20 md:pt-24 md:pb-32 overflow-hidden">
        <div className="max-w-5xl mx-auto px-6 text-center">
          
          {/* Subheader Pill */}
          <div className="inline-flex items-center space-x-2 bg-amber-50/80 border border-amber-200/70 text-amber-900 text-xs font-semibold px-4 py-1.5 rounded-full mb-8 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-amber-600 animate-spin-slow" />
            <span>Multimodal Vision AI for DIY Makers & Hobbyists</span>
          </div>

          {/* Huge Hook Headline */}
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-stone-900 leading-[1.08] mb-8">
            Bring the image & <br />
            <span className="relative inline-block text-amber-700">
              <span className="relative z-10 italic font-serif font-normal">we find you tutorials.</span>
              <span className="absolute bottom-1 left-0 w-full h-3 bg-amber-200/60 -z-0 rounded-sm -rotate-1"></span>
            </span>
          </h1>

          {/* Subtitle Description */}
          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-stone-600 font-normal leading-relaxed mb-10">
            Saw a stunning crochet plushie, origami sculpture, or woodworking project on Pinterest or Instagram? 
            Just right-click any image. Link Hunter dissects the materials, technique, and serves the highest-rated YouTube tutorials to build it.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-14">
            <a 
              href="#interactive-demo"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-3 bg-stone-900 hover:bg-stone-800 text-white font-medium text-base px-8 py-4 rounded-2xl shadow-lg shadow-stone-900/15 transition-all hover:-translate-y-0.5 active:translate-y-0"
            >
              <span>Try Live Interactive Demo</span>
              <ArrowRight className="w-4 h-4" />
            </a>

            <a 
              href="#how-it-works"
              className="w-full sm:w-auto inline-flex items-center justify-center space-x-2 bg-white hover:bg-stone-50 border border-stone-200 text-stone-700 font-medium text-base px-7 py-4 rounded-2xl shadow-sm hover:shadow transition-all"
            >
              <span>See How it Works</span>
              <ChevronRight className="w-4 h-4 text-stone-400" />
            </a>
          </div>

          {/* Trust Metrics / Micro-proof */}
          <div className="pt-8 border-t border-stone-200/60 flex flex-wrap items-center justify-center gap-8 text-xs font-semibold text-stone-500 uppercase tracking-wider">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Right-Click from any tab</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>100% Free for crafters</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Cosine Semantic Filtering</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>No more keyword guessing</span>
            </div>
          </div>

        </div>
      </section>

      {/* Interactive Live Demo Sandbox */}
      <section id="interactive-demo" className="relative z-10 py-16 bg-white border-y border-stone-200/80">
        <div className="max-w-6xl mx-auto px-6">
          
          <div className="text-center max-w-2xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              Interactive Showcase
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight mt-3 mb-4">
              Experience the Vision Pipeline in Real Time
            </h2>
            <p className="text-stone-600 text-base">
              Select one of the community craft samples below to see how Link Hunter deconstructs the image, generates query intent, and semantically curates tutorials.
            </p>
          </div>

          {/* Sample Selector Tabs */}
          <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
            {SAMPLES.map((sample) => (
              <button
                key={sample.id}
                onClick={() => setSelectedSample(sample)}
                className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all ${
                  selectedSample.id === sample.id
                    ? 'bg-amber-600 text-white shadow-md shadow-amber-600/20'
                    : 'bg-stone-100 hover:bg-stone-200 text-stone-700 border border-stone-200'
                }`}
              >
                <span>{sample.id === 'crochet' ? '🧶' : sample.id === 'origami' ? '📜' : '🪵'}</span>
                <span>{sample.title}</span>
              </button>
            ))}
          </div>

          {/* Main Visual Demo Card */}
          <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-6 md:p-8 shadow-xl shadow-stone-200/50">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* Left Column: Input Image & Extracted Metadata */}
              <div className="lg:col-span-5 space-y-5">
                <div className="relative group overflow-hidden rounded-2xl border border-stone-300/80 bg-white shadow-sm">
                  <img 
                    src={selectedSample.imageUrl} 
                    alt={selectedSample.title}
                    className="w-full h-64 object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute top-3 left-3 bg-stone-900/80 backdrop-blur-md text-white text-[11px] font-medium px-3 py-1 rounded-full flex items-center space-x-1.5">
                    <MousePointerClick className="w-3.5 h-3.5 text-amber-400" />
                    <span>Right-Clicked Image</span>
                  </div>
                </div>

                {/* AI Detection Card */}
                <div className="bg-white rounded-2xl p-5 border border-stone-200 space-y-3.5 shadow-sm">
                  <div className="flex items-center justify-between border-b border-stone-100 pb-3">
                    <span className="text-xs font-bold text-stone-500 uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-amber-600" />
                      Multimodal Vision Analysis
                    </span>
                    <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      is_valid: true
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div>
                      <p className="text-stone-400 font-medium">Category</p>
                      <p className="font-semibold text-stone-800">{selectedSample.category}</p>
                    </div>
                    <div>
                      <p className="text-stone-400 font-medium">Materials</p>
                      <p className="font-semibold text-stone-800 truncate" title={selectedSample.materials}>{selectedSample.materials}</p>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-stone-100">
                    <p className="text-[11px] text-stone-400 font-medium mb-1">Optimized YouTube Search Query</p>
                    <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl px-3 py-2 text-xs font-mono font-medium text-amber-900 flex items-center justify-between">
                      <span className="truncate">"{selectedSample.query}"</span>
                      <Search className="w-3.5 h-3.5 text-amber-600 shrink-0 ml-2" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Simulated Extension Popup Results */}
              <div className="lg:col-span-7">
                <div className="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm">
                  
                  {/* Extension Header Simulation */}
                  <div className="flex items-center justify-between border-b border-stone-200/80 pb-4 mb-5">
                    <div className="flex items-center space-x-2">
                      <div className="w-7 h-7 rounded-lg bg-amber-500 text-white flex items-center justify-center text-xs font-bold shadow-sm">
                        LH
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-stone-900">Curated Video Tutorials</h4>
                        <p className="text-[11px] text-stone-500">Ranked by Cosine Relevance & Popularity Decay</p>
                      </div>
                    </div>
                    <span className="text-xs font-semibold text-stone-600 bg-stone-100 px-2.5 py-1 rounded-full border border-stone-200">
                      {selectedSample.results.length} Videos Found
                    </span>
                  </div>

                  {/* Video Results List */}
                  <div className="space-y-4">
                    {selectedSample.results.map((video, idx) => (
                      <div 
                        key={idx}
                        className="group flex flex-col sm:flex-row gap-4 p-3.5 rounded-xl border border-stone-100 hover:border-amber-200 hover:bg-amber-50/30 transition-all cursor-pointer"
                      >
                        <div className="relative sm:w-40 h-24 rounded-lg overflow-hidden shrink-0 bg-stone-100">
                          <img 
                            src={video.thumbnail} 
                            alt={video.title} 
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                          <div className="absolute bottom-1.5 right-1.5 bg-black/80 backdrop-blur text-white text-[10px] font-medium px-1.5 py-0.5 rounded">
                            {video.duration}
                          </div>
                        </div>

                        <div className="flex-1 flex flex-col justify-between">
                          <div>
                            <div className="flex items-center justify-between gap-2 mb-1">
                              <span className="text-[11px] font-semibold text-stone-500">{video.channel}</span>
                              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                                {video.match}
                              </span>
                            </div>
                            <h5 className="text-xs sm:text-sm font-semibold text-stone-900 group-hover:text-amber-800 line-clamp-2 leading-snug">
                              {video.title}
                            </h5>
                          </div>

                          <div className="flex items-center space-x-4 text-[11px] text-stone-500 font-medium pt-2">
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3 text-stone-400" />
                              {video.views}
                            </span>
                            <span className="flex items-center gap-1">
                              <Flame className="w-3 h-3 text-amber-500" />
                              Score: {video.score}
                            </span>
                            <span className="text-amber-700 font-semibold group-hover:underline flex items-center gap-0.5 ml-auto">
                              Watch <ExternalLink className="w-3 h-3 ml-0.5" />
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Micro Footer inside Card */}
                  <div className="mt-5 pt-4 border-t border-stone-100 flex items-center justify-between text-xs text-stone-500">
                    <span className="flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-emerald-600" />
                      Zero clickbait: Filtered with Google Gemini embeddings
                    </span>
                    <span className="font-semibold text-stone-700">Link Hunter v1.0</span>
                  </div>

                </div>
              </div>

            </div>
          </div>

        </div>
      </section>

      {/* How It Works (3 Steps) */}
      <section id="how-it-works" className="relative z-10 py-24 bg-[#FAF8F5]">
        <div className="max-w-6xl mx-auto px-6">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              Effortless Workflow
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight mt-3 mb-4">
              From Discovery to Hands-On Crafting in 3 Clicks
            </h2>
            <p className="text-stone-600 text-base">
              Stop typing vague descriptions like "green wool thing tutorial". Let AI see the craft details for you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Step 1 */}
            <div className="bg-white rounded-3xl p-8 border border-stone-200/80 shadow-sm hover:shadow-md transition-shadow relative">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 font-bold text-lg mb-6">
                01
              </div>
              <h3 className="text-xl font-bold text-stone-900 mb-3">Right-Click Any Image</h3>
              <p className="text-stone-600 text-sm leading-relaxed">
                Browse Pinterest, Instagram, Etsy, or DIY blogs. When you spot an item you want to make, simply right-click and choose <strong>"Search with LH"</strong>.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-white rounded-3xl p-8 border border-stone-200/80 shadow-sm hover:shadow-md transition-shadow relative">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 font-bold text-lg mb-6">
                02
              </div>
              <h3 className="text-xl font-bold text-stone-900 mb-3">AI Vision Deconstructs</h3>
              <p className="text-stone-600 text-sm leading-relaxed">
                Our vision pipeline parses raw pixels to identify craft type (crochet, origami, woodwork), required materials, and crafts high-intent search queries.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-white rounded-3xl p-8 border border-stone-200/80 shadow-sm hover:shadow-md transition-shadow relative">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 font-bold text-lg mb-6">
                03
              </div>
              <h3 className="text-xl font-bold text-stone-900 mb-3">Curated YouTube Tutorials</h3>
              <p className="text-stone-600 text-sm leading-relaxed">
                Cosine similarity filters out irrelevant vlogs while a freshness formula balances viral classics with pristine new HD tutorials.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* Feature Bento Grid */}
      <section id="pipeline" className="relative z-10 py-24 bg-white border-t border-stone-200">
        <div className="max-w-6xl mx-auto px-6">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              Engineering Excellence
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight mt-3 mb-4">
              Under the Hood of the Craft Intelligence Engine
            </h2>
            <p className="text-stone-600 text-base">
              A high-performance pipeline tuned to bridge the gap between creative visual inspiration and actionable YouTube instructional videos.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            
            {/* Bento Card 1 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-amber-800 mb-5">
                  <Sparkles className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">Multimodal Vision LLM</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Powered by Google Gemma/Gemini vision models to accurately separate genuine handmade DIY projects from factory-manufactured commercial goods.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-amber-900">
                model: gemma-4-26b-a4b-it
              </div>
            </div>

            {/* Bento Card 2 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center text-emerald-800 mb-5">
                  <Filter className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">Batch Vector Embeddings</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Embeds search query and 20 candidate video titles simultaneously via 768-dimensional vectors, executing cosine similarity checks in under 0.4 seconds.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-emerald-900">
                gemini-embedding-001 (768d)
              </div>
            </div>

            {/* Bento Card 3 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-rose-100 flex items-center justify-center text-rose-800 mb-5">
                  <Flame className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">Mathematical Freshness Decay</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Scores every tutorial using a custom formula: <code className="bg-white px-1.5 py-0.5 rounded border text-stone-800">Views / (1.2 ^ YearsOld)</code> to prevent old low-res videos from dominating your feed.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-rose-900">
                Formula: Popularity ÷ 1.2^Years
              </div>
            </div>

            {/* Bento Card 4 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center text-blue-800 mb-5">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">JWT Security & Storage</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Stateless JWT access tokens with bcrypt salted hashes stored securely in MongoDB Atlas, safeguarding your search histories and preferences.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-blue-900">
                HS256 Auth & MongoDB Atlas
              </div>
            </div>

            {/* Bento Card 5 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center text-purple-800 mb-5">
                  <Zap className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">Containerized FastAPI</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Lightweight ASGI microservice running asynchronously under Uvicorn inside minimal Linux AMD64 containers deployed seamlessly on Render.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-purple-900">
                Docker / Python 3.12-slim
              </div>
            </div>

            {/* Bento Card 6 */}
            <div className="bg-[#FAF8F5] border border-stone-200 rounded-3xl p-7 flex flex-col justify-between">
              <div>
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-amber-800 mb-5">
                  <Award className="w-5 h-5" />
                </div>
                <h4 className="text-lg font-bold text-stone-900 mb-2">LangSmith Tracing</h4>
                <p className="text-stone-600 text-sm leading-relaxed">
                  Full production telemetry tracking time-to-first-token, batch embedding latency, and API execution spans via LangSmith's observability suite.
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-stone-200/60 text-xs font-mono text-amber-900">
                @traceable End-to-End Tracing
              </div>
            </div>

          </div>

        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section id="faq" className="relative z-10 py-24 bg-[#FAF8F5]">
        <div className="max-w-4xl mx-auto px-6">
          
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-widest text-amber-700 bg-amber-50 px-3 py-1 rounded-full border border-amber-200">
              Clear Answers
            </span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight mt-3 mb-4">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-4">
            
            <div className="bg-white rounded-2xl p-6 border border-stone-200 shadow-sm">
              <h4 className="text-base font-bold text-stone-900 mb-2">
                How is Link Hunter different from Google Lens or Pinterest Visual Search?
              </h4>
              <p className="text-stone-600 text-sm leading-relaxed">
                Google Lens and Pinterest visual search try to find where to <em>buy</em> the product or match similar photos. Link Hunter is built specifically for <strong>makers</strong>: it identifies the craft technique, primary materials, and finds <strong>how to make it</strong> via curated YouTube step-by-step video tutorials.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-stone-200 shadow-sm">
              <h4 className="text-base font-bold text-stone-900 mb-2">
                Does it work on Instagram, Pinterest, and Reddit?
              </h4>
              <p className="text-stone-600 text-sm leading-relaxed">
                Yes! Any webpage where you can right-click an image works. The Chrome Extension context menu captures the image source and delivers your tutorials directly to your extension popup.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-stone-200 shadow-sm">
              <h4 className="text-base font-bold text-stone-900 mb-2">
                What crafts and DIY disciplines are supported?
              </h4>
              <p className="text-stone-600 text-sm leading-relaxed">
                Link Hunter excels at crochet & knitting, origami & papercraft, woodworking & whittling, leathercraft, polymer clay & resin pouring, pottery, cross-stitch, jewelry making, and 3D printing crafts.
              </p>
            </div>

            <div className="bg-white rounded-2xl p-6 border border-stone-200 shadow-sm">
              <h4 className="text-base font-bold text-stone-900 mb-2">
                What happens if I click on a picture of a commercial car or nature?
              </h4>
              <p className="text-stone-600 text-sm leading-relaxed">
                Our vision model will gracefully reject non-DIY items (returning <code className="text-xs bg-stone-100 px-1 py-0.5 rounded">is_valid: false</code>) with a friendly explanation, advising you to select a handmade craft object instead.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* Bottom CTA Banner */}
      <section className="relative z-10 py-20 bg-stone-900 text-white">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <span className="text-amber-400 text-xs font-semibold uppercase tracking-widest bg-amber-950/60 border border-amber-800/60 px-3 py-1 rounded-full">
            Start Crafting Today
          </span>
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight mt-4 mb-6">
            Ready to bring your creative inspiration to life?
          </h2>
          <p className="text-stone-300 text-base sm:text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
            Install the free Chrome extension and discover the exact tutorials behind any handmade craft you see online.
          </p>

          <a 
            href="https://github.com/debjitghorai/LH" 
            target="_blank" 
            rel="noreferrer"
            className="inline-flex items-center space-x-3 bg-amber-500 hover:bg-amber-400 text-stone-950 font-bold text-base px-8 py-4 rounded-2xl shadow-xl shadow-amber-500/20 transition-all hover:-translate-y-0.5"
          >
            <span>Install Link Hunter for Chrome</span>
            <ArrowRight className="w-4 h-4" />
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-stone-200 bg-[#FAF8F5] py-12">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6 text-xs text-stone-500 font-medium">
          <div className="flex items-center space-x-2">
            <span className="text-base">🧶</span>
            <span className="font-bold text-stone-900 text-sm">Link Hunter</span>
            <span>— The AI Craft Discovery Engine</span>
          </div>

          <div className="flex items-center space-x-6">
            <a href="#how-it-works" className="hover:text-stone-900 transition-colors">How it Works</a>
            <a href="#interactive-demo" className="hover:text-stone-900 transition-colors">Showcase</a>
            <a href="#pipeline" className="hover:text-stone-900 transition-colors">AI Architecture</a>
            <a href="https://github.com/debjitghorai/LH" target="_blank" rel="noreferrer" className="hover:text-stone-900 transition-colors">GitHub</a>
          </div>

          <div>
            © {new Date().getFullYear()} Link Hunter. Built for Makers & Crafters worldwide.
          </div>
        </div>
      </footer>

    </div>
  );
}

