"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useEffect } from "react";
import { useAuthStore } from "@/lib/store";
import { useRouter } from "next/navigation";

export default function Home() {
  const { hydrate, isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-grid relative overflow-hidden">
      {/* Background glow effects */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/5 rounded-full blur-3xl" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-3"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center">
            <span className="text-white font-bold text-lg">S</span>
          </div>
          <span className="text-xl font-bold neon-text">StyleSense</span>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="flex items-center gap-4"
        >
          <Link href="/login" className="btn-secondary text-sm px-6 py-2.5">
            Sign In
          </Link>
          <Link href="/register" className="btn-primary text-sm px-6 py-2.5">
            Get Started
          </Link>
        </motion.div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-7xl mx-auto px-8 pt-20 pb-32">
        <div className="flex flex-col items-center text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="mb-6"
          >
            <span className="glass inline-block px-4 py-1.5 text-sm text-purple-300 rounded-full">
              ✨ AI-Powered Fashion Intelligence
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-5xl md:text-7xl font-bold max-w-4xl leading-tight mb-6"
          >
            Your Wardrobe,{" "}
            <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent animate-gradient">
              Reimagined
            </span>{" "}
            by AI
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="text-lg md:text-xl max-w-2xl mb-10 leading-relaxed"
            style={{ color: "var(--text-secondary)" }}
          >
            Upload your clothes, get AI-powered outfit recommendations,
            color-matched combinations, and personalized styling tips — all in one place.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4"
          >
            <Link
              href="/register"
              className="btn-primary text-base px-10 py-4 rounded-2xl flex items-center gap-2"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
              Start Your Style Journey
            </Link>
            <Link
              href="/login"
              className="btn-secondary text-base px-10 py-4 rounded-2xl"
            >
              I Have an Account
            </Link>
          </motion.div>
        </div>

        {/* Feature Cards */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-28"
        >
          {[
            {
              icon: "🧠",
              title: "AI Detection",
              desc: "Upload clothing images and let AI detect categories, extract dominant colors, and catalog your wardrobe automatically.",
              color: "from-purple-500/20 to-purple-500/0",
            },
            {
              icon: "👔",
              title: "Smart Outfits",
              desc: "Get scored outfit combinations based on color harmony, your body type, gender, and the occasion you're dressing for.",
              color: "from-blue-500/20 to-blue-500/0",
            },
            {
              icon: "💡",
              title: "Styling Tips",
              desc: "Receive personalized accessory suggestions, footwear pairing, do's & don'ts, and grooming tips for each outfit.",
              color: "from-cyan-500/20 to-cyan-500/0",
            },
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.9 + i * 0.1 }}
              className="glass-card p-8 relative overflow-hidden group"
            >
              <div
                className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
              />
              <div className="relative z-10">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p style={{ color: "var(--text-secondary)" }} className="leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom accent */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.2 }}
          className="mt-20 text-center"
          style={{ color: "var(--text-muted)" }}
        >
          <p className="text-sm">
            Built with Next.js • FastAPI • AI-Powered Recommendations
          </p>
        </motion.div>
      </main>
    </div>
  );
}
