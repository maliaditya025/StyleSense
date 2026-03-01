"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAuthStore, useClosetStore, useOutfitStore } from "@/lib/store";
import { getCloset, getSavedOutfits } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
    const { user } = useAuthStore();
    const { clothes, setClothes } = useClosetStore();
    const { outfits, setOutfits } = useOutfitStore();
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        async function loadData() {
            try {
                const [closetData, outfitData] = await Promise.all([
                    getCloset(),
                    getSavedOutfits(),
                ]);
                setClothes(closetData);
                setOutfits(outfitData);
            } catch (e) {
                console.error("Failed to load dashboard data", e);
            } finally {
                setLoaded(true);
            }
        }
        loadData();
    }, [setClothes, setOutfits]);

    const stats = [
        { label: "Clothing Items", value: clothes.length, icon: "👕", color: "from-purple-500/20 to-purple-500/5" },
        { label: "Outfits Generated", value: outfits.length, icon: "✨", color: "from-blue-500/20 to-blue-500/5" },
        { label: "Categories", value: new Set(clothes.map((c) => c.category)).size, icon: "📂", color: "from-cyan-500/20 to-cyan-500/5" },
        { label: "Avg Score", value: outfits.length ? Math.round(outfits.reduce((a, o) => a + o.score, 0) / outfits.length) : 0, icon: "🏆", color: "from-green-500/20 to-green-500/5" },
    ];

    return (
        <div>
            {/* Welcome */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="mb-10"
            >
                <h1 className="text-3xl md:text-4xl font-bold mb-2">
                    Welcome back, <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">{user?.name?.split(" ")[0] || "there"}</span>
                </h1>
                <p style={{ color: "var(--text-secondary)" }}>Here&apos;s an overview of your style profile</p>
            </motion.div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
                {stats.map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: i * 0.1 }}
                        className={`glass-card p-6 relative overflow-hidden bg-gradient-to-br ${stat.color}`}
                    >
                        <div className="text-3xl mb-3">{stat.icon}</div>
                        <div className="text-3xl font-bold mb-1">{loaded ? stat.value : "—"}</div>
                        <div className="text-sm" style={{ color: "var(--text-secondary)" }}>{stat.label}</div>
                    </motion.div>
                ))}
            </div>

            {/* Quick Actions */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="mb-10"
            >
                <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Link href="/upload" className="glass-card p-6 flex items-center gap-4 group cursor-pointer">
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                            📷
                        </div>
                        <div>
                            <h3 className="font-semibold mb-0.5">Upload Clothes</h3>
                            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Add items to your closet</p>
                        </div>
                    </Link>

                    <Link href="/recommendations" className="glass-card p-6 flex items-center gap-4 group cursor-pointer">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                            ✨
                        </div>
                        <div>
                            <h3 className="font-semibold mb-0.5">Get Recommendations</h3>
                            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>AI-powered outfit combos</p>
                        </div>
                    </Link>

                    <Link href="/closet" className="glass-card p-6 flex items-center gap-4 group cursor-pointer">
                        <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                            👕
                        </div>
                        <div>
                            <h3 className="font-semibold mb-0.5">View Closet</h3>
                            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Browse your wardrobe</p>
                        </div>
                    </Link>
                </div>
            </motion.div>

            {/* Recent Outfits */}
            {outfits.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.5 }}
                >
                    <h2 className="text-xl font-semibold mb-4">Recent Outfits</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {outfits.slice(0, 3).map((outfit) => (
                            <div key={outfit.id} className="glass-card p-5">
                                <div className="flex items-center justify-between mb-4">
                                    <span className="text-sm px-3 py-1 rounded-full bg-purple-500/15 text-purple-300">
                                        {outfit.occasion || "casual"}
                                    </span>
                                    <div className="score-badge text-xs">{Math.round(outfit.score)}</div>
                                </div>
                                <div className="flex gap-2 mb-3">
                                    {outfit.items.map((item) => (
                                        <div
                                            key={item.id}
                                            className="w-10 h-10 rounded-lg border border-white/10"
                                            style={{ backgroundColor: item.primary_color }}
                                            title={item.category}
                                        />
                                    ))}
                                </div>
                                {outfit.tips && outfit.tips.length > 0 && (
                                    <p className="text-xs leading-relaxed" style={{ color: "var(--text-secondary)" }}>
                                        💡 {outfit.tips[0]}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Empty state */}
            {loaded && clothes.length === 0 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.5 }}
                    className="text-center py-16"
                >
                    <div className="text-6xl mb-4">👗</div>
                    <h3 className="text-xl font-semibold mb-2">Your closet is empty</h3>
                    <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
                        Upload some clothing items to get started with AI recommendations
                    </p>
                    <Link href="/upload" className="btn-primary px-8 py-3 inline-block">
                        Upload Your First Item
                    </Link>
                </motion.div>
            )}
        </div>
    );
}
