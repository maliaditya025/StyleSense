"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useAuthStore } from "@/lib/store";

const NAV_ITEMS = [
    { href: "/dashboard", label: "Dashboard", icon: "📊" },
    { href: "/upload", label: "Upload", icon: "📷" },
    { href: "/closet", label: "My Closet", icon: "👕" },
    { href: "/recommendations", label: "Outfits", icon: "✨" },
    { href: "/tryon", label: "3D Try-On", icon: "🎭" },
    { href: "/profile", label: "Profile", icon: "👤" },
];

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
    const { hydrate, isAuthenticated, user, logout } = useAuthStore();
    const router = useRouter();
    const pathname = usePathname();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        hydrate();
    }, [hydrate]);

    useEffect(() => {
        // Slight delay to let hydration complete
        const timer = setTimeout(() => {
            const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
            if (!token) {
                router.push("/login");
            }
        }, 100);
        return () => clearTimeout(timer);
    }, [router]);

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    return (
        <div className="min-h-screen flex">
            {/* Mobile sidebar overlay */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/60 z-40 md:hidden"
                        onClick={() => setSidebarOpen(false)}
                    />
                )}
            </AnimatePresence>

            {/* Sidebar */}
            <aside
                className={`fixed md:sticky top-0 left-0 h-screen z-50 transition-transform duration-300
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"}`}
                style={{ width: "var(--sidebar-width)" }}
            >
                <div className="h-full glass-strong flex flex-col p-5 rounded-none md:rounded-r-2xl border-l-0">
                    {/* Logo */}
                    <div className="flex items-center gap-3 mb-10">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shrink-0">
                            <span className="text-white font-bold text-lg">S</span>
                        </div>
                        <span className="text-lg font-bold neon-text">StyleSense</span>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 space-y-1">
                        {NAV_ITEMS.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setSidebarOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                    ${isActive
                                            ? "bg-purple-500/15 text-purple-300 border border-purple-500/20"
                                            : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
                                        }`}
                                >
                                    <span className="text-lg">{item.icon}</span>
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>

                    {/* User section */}
                    <div className="pt-4 border-t border-white/5">
                        <div className="flex items-center gap-3 px-3 py-2 mb-3">
                            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500/40 to-blue-500/40 flex items-center justify-center text-sm font-bold">
                                {user?.name?.charAt(0)?.toUpperCase() || "U"}
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium truncate">{user?.name || "User"}</p>
                                <p className="text-xs truncate" style={{ color: "var(--text-muted)" }}>
                                    {user?.email || ""}
                                </p>
                            </div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                        >
                            <span>🚪</span>
                            Sign Out
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 min-h-screen">
                {/* Mobile topbar */}
                <div className="md:hidden flex items-center justify-between p-4 glass-strong sticky top-0 z-30">
                    <button
                        onClick={() => setSidebarOpen(true)}
                        className="p-2 hover:bg-white/5 rounded-lg transition-colors"
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 12h18M3 6h18M3 18h18" />
                        </svg>
                    </button>
                    <span className="font-bold neon-text">StyleSense</span>
                    <div className="w-10" />
                </div>

                {/* Page content with animation */}
                <motion.div
                    key={pathname}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className="p-6 md:p-10 max-w-7xl"
                >
                    {children}
                </motion.div>
            </main>
        </div>
    );
}
