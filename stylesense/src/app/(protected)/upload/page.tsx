"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { uploadClothes, getImageUrl } from "@/lib/api";
import { useClosetStore } from "@/lib/store";
import type { Clothing } from "@/lib/types";

const CATEGORIES = [
    "shirt", "t-shirt", "pants", "jeans", "shoes",
    "jacket", "dress", "accessories", "shorts", "skirt",
];

export default function UploadPage() {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState<Clothing | null>(null);
    const [selectedCategory, setSelectedCategory] = useState<string>("");
    const [error, setError] = useState("");
    const { addItem } = useClosetStore();

    const handleFile = useCallback((f: File) => {
        if (!f.type.startsWith("image/")) {
            setError("Please upload an image file");
            return;
        }
        setFile(f);
        setPreview(URL.createObjectURL(f));
        setResult(null);
        setSelectedCategory("");
        setError("");
    }, []);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(e.type === "dragenter" || e.type === "dragover");
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError("");
        try {
            const clothing = await uploadClothes(
                file,
                selectedCategory || undefined
            );
            setResult(clothing);
            addItem(clothing);
        } catch (err: any) {
            setError(err.response?.data?.detail || "Upload failed");
        } finally {
            setUploading(false);
        }
    };

    const resetForm = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setSelectedCategory("");
        setError("");
    };

    // Format confidence as percentage
    const confidenceLabel = (score?: number | null) => {
        if (score == null) return null;
        const pct = Math.round(score * 100);
        const color = pct >= 70 ? "text-green-400" : pct >= 40 ? "text-yellow-400" : "text-red-400";
        return <span className={`${color} font-medium`}>{pct}%</span>;
    };

    return (
        <div className="max-w-2xl">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-3xl font-bold mb-2">Upload Clothing</h1>
                <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
                    Upload an image and our CNN model will detect the category and extract colors
                </p>

                {/* Drop zone */}
                {!preview && (
                    <div
                        onDragEnter={handleDrag}
                        onDragLeave={handleDrag}
                        onDragOver={handleDrag}
                        onDrop={handleDrop}
                        className={`relative glass-card p-12 text-center cursor-pointer transition-all duration-300
              ${dragActive ? "border-purple-500/60 bg-purple-500/5 scale-[1.02]" : "hover:border-purple-500/30"}`}
                    >
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                        />
                        <div className="text-5xl mb-4">📷</div>
                        <h3 className="text-lg font-semibold mb-2">
                            {dragActive ? "Drop it here!" : "Drag & Drop or Click to Upload"}
                        </h3>
                        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                            Supports JPG, PNG, WebP • Max 10MB
                        </p>
                    </div>
                )}

                {/* Preview + Category selector + Results */}
                <AnimatePresence>
                    {preview && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="glass-card p-6"
                        >
                            <div className="flex flex-col md:flex-row gap-6">
                                <div className="w-full md:w-64 h-64 rounded-xl overflow-hidden bg-white/5">
                                    <img
                                        src={preview}
                                        alt="Preview"
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <div className="flex-1">
                                    {result ? (
                                        /* ─── After upload: show CNN results ─── */
                                        <div>
                                            <h3 className="text-lg font-semibold mb-3">🧠 CNN Detection Results</h3>
                                            <div className="space-y-3">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-sm" style={{ color: "var(--text-secondary)" }}>Category:</span>
                                                    <span className="px-3 py-1 rounded-full bg-purple-500/15 text-purple-300 text-sm font-medium capitalize">
                                                        {result.category}
                                                    </span>
                                                </div>
                                                {result.confidence_score != null && (
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-sm" style={{ color: "var(--text-secondary)" }}>Confidence:</span>
                                                        <div className="flex items-center gap-2">
                                                            {confidenceLabel(result.confidence_score)}
                                                            <div className="w-24 h-2 bg-white/10 rounded-full overflow-hidden">
                                                                <div
                                                                    className="h-full rounded-full transition-all duration-500"
                                                                    style={{
                                                                        width: `${Math.round(result.confidence_score * 100)}%`,
                                                                        backgroundColor: result.confidence_score >= 0.7
                                                                            ? "#4ade80"
                                                                            : result.confidence_score >= 0.4
                                                                                ? "#facc15"
                                                                                : "#f87171",
                                                                    }}
                                                                />
                                                            </div>
                                                        </div>
                                                    </div>
                                                )}
                                                <div className="flex items-center gap-3">
                                                    <span className="text-sm" style={{ color: "var(--text-secondary)" }}>Primary Color:</span>
                                                    <div className="flex items-center gap-2">
                                                        <div className="color-swatch" style={{ backgroundColor: result.primary_color }} />
                                                        <span className="text-sm">{result.color_name || result.primary_color}</span>
                                                    </div>
                                                </div>
                                                {result.secondary_color && (
                                                    <div className="flex items-center gap-3">
                                                        <span className="text-sm" style={{ color: "var(--text-secondary)" }}>Secondary:</span>
                                                        <div className="flex items-center gap-2">
                                                            <div className="color-swatch" style={{ backgroundColor: result.secondary_color }} />
                                                            <span className="text-sm">{result.secondary_color}</span>
                                                        </div>
                                                    </div>
                                                )}
                                                <div className="pt-3 mt-3 border-t border-white/5">
                                                    <p className="text-sm text-green-400 flex items-center gap-2">
                                                        ✅ Added to your closet!
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ) : (
                                        /* ─── Before upload: category selector ─── */
                                        <div>
                                            <h3 className="text-lg font-semibold mb-2">Select Category</h3>
                                            <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
                                                Choose a category or let the CNN model detect it automatically
                                            </p>
                                            <div className="flex flex-wrap gap-2 mb-4">
                                                <button
                                                    onClick={() => setSelectedCategory("")}
                                                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200
                                                        ${!selectedCategory
                                                            ? "bg-purple-500/30 text-purple-200 ring-1 ring-purple-500/50"
                                                            : "bg-white/5 text-white/60 hover:bg-white/10"
                                                        }`}
                                                >
                                                    🧠 CNN Auto-detect
                                                </button>
                                                {CATEGORIES.map((cat) => (
                                                    <button
                                                        key={cat}
                                                        onClick={() => setSelectedCategory(cat)}
                                                        className={`px-3 py-1.5 rounded-full text-xs font-medium capitalize transition-all duration-200
                                                            ${selectedCategory === cat
                                                                ? "bg-purple-500/30 text-purple-200 ring-1 ring-purple-500/50"
                                                                : "bg-white/5 text-white/60 hover:bg-white/10"
                                                            }`}
                                                    >
                                                        {cat}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <div className="flex gap-3 mt-4">
                                        {!result && (
                                            <button
                                                onClick={handleUpload}
                                                disabled={uploading}
                                                className="btn-primary px-6 py-2.5 text-sm disabled:opacity-50"
                                            >
                                                {uploading ? (
                                                    <span className="flex items-center gap-2">
                                                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                        </svg>
                                                        Analyzing...
                                                    </span>
                                                ) : selectedCategory ? (
                                                    `📤 Upload as ${selectedCategory}`
                                                ) : (
                                                    "🧠 Upload & Auto-detect"
                                                )}
                                            </button>
                                        )}
                                        <button onClick={resetForm} className="btn-secondary px-6 py-2.5 text-sm">
                                            {result ? "Upload Another" : "Cancel"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Error */}
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
                    >
                        {error}
                    </motion.div>
                )}
            </motion.div>
        </div>
    );
}
