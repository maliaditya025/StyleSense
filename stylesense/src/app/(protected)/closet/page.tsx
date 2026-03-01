"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getCloset, deleteClothing, getImageUrl } from "@/lib/api";
import { useClosetStore } from "@/lib/store";

const CATEGORIES = ["all", "shirt", "t-shirt", "pants", "jeans", "shoes", "jacket", "dress", "accessories", "shorts", "skirt"];

export default function ClosetPage() {
    const { clothes, setClothes, removeItem, setLoading, isLoading } = useClosetStore();
    const [filter, setFilter] = useState("all");
    const [deleting, setDeleting] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            setLoading(true);
            try {
                const data = await getCloset();
                setClothes(data);
            } catch (e) {
                console.error("Failed to load closet", e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, [setClothes, setLoading]);

    const filtered = filter === "all" ? clothes : clothes.filter((c) => c.category === filter);

    const handleDelete = async (id: string) => {
        setDeleting(id);
        try {
            await deleteClothing(id);
            removeItem(id);
        } catch (e) {
            console.error("Failed to delete", e);
        } finally {
            setDeleting(null);
        }
    };

    return (
        <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-1">My Closet</h1>
                        <p style={{ color: "var(--text-secondary)" }}>
                            {clothes.length} item{clothes.length !== 1 ? "s" : ""} in your wardrobe
                        </p>
                    </div>
                </div>

                {/* Category Filter */}
                <div className="flex gap-2 flex-wrap mb-8">
                    {CATEGORIES.map((cat) => (
                        <button
                            key={cat}
                            onClick={() => setFilter(cat)}
                            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all capitalize
                ${filter === cat
                                    ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                                    : "glass-card text-slate-400 hover:text-slate-200 border border-transparent"
                                }`}
                        >
                            {cat === "all" ? `All (${clothes.length})` : cat}
                        </button>
                    ))}
                </div>

                {/* Grid */}
                {isLoading ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {[...Array(8)].map((_, i) => (
                            <div key={i} className="glass-card p-4 animate-pulse">
                                <div className="w-full aspect-square rounded-xl bg-white/5 mb-3" />
                                <div className="h-4 bg-white/5 rounded w-2/3 mb-2" />
                                <div className="h-3 bg-white/5 rounded w-1/2" />
                            </div>
                        ))}
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="text-center py-16">
                        <div className="text-5xl mb-3">👔</div>
                        <h3 className="text-lg font-semibold mb-1">
                            {filter !== "all" ? `No ${filter} items yet` : "No items in your closet"}
                        </h3>
                        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                            Upload some clothing to get started
                        </p>
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        <AnimatePresence>
                            {filtered.map((item, i) => (
                                <motion.div
                                    key={item.id}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="glass-card p-4 group relative"
                                >
                                    <div className="w-full aspect-square rounded-xl overflow-hidden bg-white/5 mb-3">
                                        <img
                                            src={getImageUrl(item.image_url)}
                                            alt={item.category}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="font-medium text-sm capitalize">{item.category}</p>
                                            <div className="flex items-center gap-1.5 mt-1">
                                                <div className="color-swatch w-4 h-4" style={{ backgroundColor: item.primary_color }} />
                                                <span className="text-xs" style={{ color: "var(--text-muted)" }}>
                                                    {item.color_name || item.primary_color}
                                                </span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDelete(item.id)}
                                            disabled={deleting === item.id}
                                            className="opacity-0 group-hover:opacity-100 p-2 hover:bg-red-500/10 rounded-lg transition-all text-red-400 text-sm"
                                        >
                                            {deleting === item.id ? "..." : "🗑"}
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </motion.div>
        </div>
    );
}
