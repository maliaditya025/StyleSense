"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { generateOutfits, getStylingTips, getImageUrl } from "@/lib/api";
import { useOutfitStore } from "@/lib/store";
import type { Outfit, StylingTips } from "@/lib/types";

const OCCASIONS = [
    { value: "casual", label: "Casual", icon: "👕" },
    { value: "formal", label: "Formal", icon: "👔" },
    { value: "party", label: "Party", icon: "🎉" },
    { value: "work", label: "Work", icon: "💼" },
    { value: "date", label: "Date", icon: "💕" },
    { value: "vacation", label: "Vacation", icon: "🏖" },
    { value: "gym", label: "Gym", icon: "🏋️" },
];

const WEATHER = [
    { value: "", label: "Any", icon: "🌤" },
    { value: "hot", label: "Hot", icon: "🔥" },
    { value: "warm", label: "Warm", icon: "☀️" },
    { value: "cold", label: "Cold", icon: "❄️" },
    { value: "rainy", label: "Rainy", icon: "🌧" },
];

const TIME_OF_DAY = [
    { value: "", label: "Any", icon: "⏰" },
    { value: "morning", label: "Morning", icon: "🌅" },
    { value: "afternoon", label: "Afternoon", icon: "☀️" },
    { value: "evening", label: "Evening", icon: "🌇" },
    { value: "night", label: "Night", icon: "🌙" },
];

const LOCATIONS = [
    { value: "", label: "Any", icon: "📍" },
    { value: "indoor", label: "Indoor", icon: "🏢" },
    { value: "outdoor", label: "Outdoor", icon: "🌳" },
];

export default function RecommendationsPage() {
    const { outfits, setOutfits, selectedOccasion, setOccasion, isLoading, setLoading } = useOutfitStore();
    const [error, setError] = useState("");
    const [selectedOutfit, setSelectedOutfit] = useState<Outfit | null>(null);
    const [tips, setTips] = useState<StylingTips | null>(null);
    const [loadingTips, setLoadingTips] = useState(false);
    const [weather, setWeather] = useState("");
    const [timeOfDay, setTimeOfDay] = useState("");
    const [location, setLocation] = useState("");

    const handleGenerate = async () => {
        setLoading(true);
        setError("");
        setSelectedOutfit(null);
        setTips(null);
        try {
            const data = await generateOutfits({ occasion: selectedOccasion, weather, time_of_day: timeOfDay, location });
            setOutfits(data);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Failed to generate outfits. Make sure you have at least 2 items in your closet.");
        } finally {
            setLoading(false);
        }
    };

    const handleViewTips = async (outfit: Outfit) => {
        setSelectedOutfit(outfit);
        setLoadingTips(true);
        try {
            const data = await getStylingTips(outfit.id);
            setTips(data);
        } catch (e) {
            console.error("Failed to load tips", e);
        } finally {
            setLoadingTips(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 75) return "from-green-500 to-emerald-500";
        if (score >= 50) return "from-blue-500 to-cyan-500";
        return "from-yellow-500 to-orange-500";
    };

    return (
        <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-3xl font-bold mb-2">Outfit Recommendations</h1>
                <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
                    AI-powered outfit combinations from your closet
                </p>

                {/* Occasion Selector */}
                <div className="mb-8">
                    <h3 className="text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>
                        What&apos;s the occasion?
                    </h3>
                    <div className="flex gap-2 flex-wrap">
                        {OCCASIONS.map((occ) => (
                            <button
                                key={occ.value}
                                onClick={() => setOccasion(occ.value)}
                                className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2
                  ${selectedOccasion === occ.value
                                        ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                                        : "glass-card text-slate-400 hover:text-slate-200"
                                    }`}
                            >
                                <span>{occ.icon}</span>
                                {occ.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Weather Selector */}
                <div className="mb-5">
                    <h3 className="text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>
                        🌤 Weather
                    </h3>
                    <div className="flex gap-2 flex-wrap">
                        {WEATHER.map((w) => (
                            <button
                                key={w.value}
                                onClick={() => setWeather(w.value)}
                                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5
                  ${weather === w.value
                                        ? "bg-sky-500/20 text-sky-300 border border-sky-500/30"
                                        : "glass-card text-slate-400 hover:text-slate-200"
                                    }`}
                            >
                                <span>{w.icon}</span>
                                {w.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Time of Day Selector */}
                <div className="mb-5">
                    <h3 className="text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>
                        🕒 Time of Day
                    </h3>
                    <div className="flex gap-2 flex-wrap">
                        {TIME_OF_DAY.map((t) => (
                            <button
                                key={t.value}
                                onClick={() => setTimeOfDay(t.value)}
                                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5
                  ${timeOfDay === t.value
                                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                        : "glass-card text-slate-400 hover:text-slate-200"
                                    }`}
                            >
                                <span>{t.icon}</span>
                                {t.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Location Selector */}
                <div className="mb-8">
                    <h3 className="text-sm font-medium mb-3" style={{ color: "var(--text-secondary)" }}>
                        📍 Location
                    </h3>
                    <div className="flex gap-2 flex-wrap">
                        {LOCATIONS.map((l) => (
                            <button
                                key={l.value}
                                onClick={() => setLocation(l.value)}
                                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-1.5
                  ${location === l.value
                                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                        : "glass-card text-slate-400 hover:text-slate-200"
                                    }`}
                            >
                                <span>{l.icon}</span>
                                {l.label}
                            </button>
                        ))}
                    </div>
                </div>

                <button
                    onClick={handleGenerate}
                    disabled={isLoading}
                    className="btn-primary px-8 py-3 mb-8 disabled:opacity-50"
                >
                    {isLoading ? (
                        <span className="flex items-center gap-2">
                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Generating outfits...
                        </span>
                    ) : (
                        "✨ Generate Outfits"
                    )}
                </button>

                {error && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    >
                        {error}
                    </motion.div>
                )}

                {/* Outfit Cards */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {outfits.map((outfit, i) => (
                        <motion.div
                            key={outfit.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className={`glass-card p-6 cursor-pointer transition-all ${selectedOutfit?.id === outfit.id ? "border-purple-500/40 ring-1 ring-purple-500/20" : ""
                                }`}
                            onClick={() => handleViewTips(outfit)}
                        >
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold">Outfit #{i + 1}</span>
                                    <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/15 text-purple-300 capitalize">
                                        {outfit.occasion}
                                    </span>
                                </div>
                                <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${getScoreColor(outfit.score)} flex items-center justify-center text-white text-sm font-bold shadow-lg`}>
                                    {Math.round(outfit.score)}
                                </div>
                            </div>

                            {/* Items */}
                            <div className="flex gap-3 mb-4">
                                {outfit.items.map((item) => (
                                    <div key={item.id} className="flex-1">
                                        <div
                                            className="w-full aspect-square rounded-xl mb-2 border border-white/10 overflow-hidden"
                                            style={{ backgroundColor: item.primary_color + "20" }}
                                        >
                                            <img
                                                src={getImageUrl(item.image_url)}
                                                alt={item.category}
                                                className="w-full h-full object-cover"
                                            />
                                        </div>
                                        <p className="text-xs text-center capitalize" style={{ color: "var(--text-secondary)" }}>
                                            {item.category}
                                        </p>
                                    </div>
                                ))}
                            </div>

                            {/* Quick tips */}
                            {outfit.tips && outfit.tips.length > 0 && (
                                <div className="pt-3 border-t border-white/5 space-y-1">
                                    {outfit.tips.slice(0, 2).map((tip, j) => (
                                        <p key={j} className="text-xs flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                            <span className="text-purple-400 mt-0.5">💡</span>
                                            {tip}
                                        </p>
                                    ))}
                                </div>
                            )}

                            <p className="text-xs mt-3 text-purple-400 opacity-70">
                                Click for detailed styling tips →
                            </p>
                        </motion.div>
                    ))}
                </div>

                {/* Detailed Tips Panel */}
                <AnimatePresence>
                    {selectedOutfit && tips && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: 20 }}
                            className="mt-6 glass-strong p-6 rounded-2xl"
                        >
                            <h3 className="text-lg font-bold mb-4">
                                💅 Styling Tips — Outfit #{outfits.indexOf(selectedOutfit) + 1}
                            </h3>

                            {loadingTips ? (
                                <div className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                    Loading styling tips...
                                </div>
                            ) : (
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    {/* General Tips */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-purple-300">💡 General Tips</h4>
                                        <ul className="space-y-2">
                                            {tips.tips.map((tip, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-purple-400 mt-1">•</span>
                                                    {tip}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Accessories */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-blue-300">💎 Accessories</h4>
                                        <ul className="space-y-2">
                                            {tips.accessories.map((acc, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-blue-400 mt-1">•</span>
                                                    {acc}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Footwear */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-cyan-300">👟 Footwear</h4>
                                        <ul className="space-y-2">
                                            {tips.footwear.map((fw, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-cyan-400 mt-1">•</span>
                                                    {fw}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Do's */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-green-300">✅ Do&apos;s</h4>
                                        <ul className="space-y-2">
                                            {tips.dos.map((d, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-green-400 mt-1">•</span>
                                                    {d}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Don'ts */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-red-300">❌ Don&apos;ts</h4>
                                        <ul className="space-y-2">
                                            {tips.donts.map((d, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-red-400 mt-1">•</span>
                                                    {d}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    {/* Grooming */}
                                    <div>
                                        <h4 className="text-sm font-semibold mb-3 text-pink-300">💈 Grooming</h4>
                                        <ul className="space-y-2">
                                            {tips.grooming.map((g, i) => (
                                                <li key={i} className="text-sm flex items-start gap-2" style={{ color: "var(--text-secondary)" }}>
                                                    <span className="text-pink-400 mt-1">•</span>
                                                    {g}
                                                </li>
                                            ))}
                                        </ul>
                                    </div>
                                </div>
                            )}
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </div>
    );
}
