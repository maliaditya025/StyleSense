"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useAuthStore } from "@/lib/store";
import { updateProfile } from "@/lib/api";
import { useRouter } from "next/navigation";
import type { Gender, BodyType, StylePreference } from "@/lib/types";

const GENDERS: { value: Gender; label: string; icon: string }[] = [
    { value: "male", label: "Male", icon: "👨" },
    { value: "female", label: "Female", icon: "👩" },
    { value: "non-binary", label: "Non-Binary", icon: "🧑" },
];

const BODY_TYPES: { value: BodyType; label: string; icon: string }[] = [
    { value: "slim", label: "Slim", icon: "🏃" },
    { value: "athletic", label: "Athletic", icon: "💪" },
    { value: "average", label: "Average", icon: "🧍" },
    { value: "plus-size", label: "Plus Size", icon: "🤗" },
];

const STYLES: { value: StylePreference; label: string; icon: string }[] = [
    { value: "casual", label: "Casual", icon: "🎽" },
    { value: "formal", label: "Formal", icon: "👔" },
    { value: "streetwear", label: "Streetwear", icon: "🧢" },
    { value: "bohemian", label: "Bohemian", icon: "🌻" },
    { value: "minimalist", label: "Minimalist", icon: "⬜" },
];

export default function ProfilePage() {
    const { user, updateUser } = useAuthStore();
    const router = useRouter();
    const [gender, setGender] = useState(user?.gender || "");
    const [bodyType, setBodyType] = useState(user?.body_type || "");
    const [style, setStyle] = useState(user?.style_preference || "");
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    const handleSave = async () => {
        setSaving(true);
        try {
            const updated = await updateProfile({
                gender: gender || undefined,
                body_type: bodyType || undefined,
                style_preference: style || undefined,
            });
            updateUser(updated);
            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
        } catch (e) {
            console.error("Failed to save profile", e);
        } finally {
            setSaving(false);
        }
    };

    const SelectionGrid = ({
        title,
        options,
        selected,
        onSelect,
    }: {
        title: string;
        options: { value: string; label: string; icon: string }[];
        selected: string;
        onSelect: (v: string) => void;
    }) => (
        <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">{title}</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {options.map((opt) => (
                    <motion.button
                        key={opt.value}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => onSelect(opt.value)}
                        className={`p-4 rounded-xl text-left transition-all duration-200
              ${selected === opt.value
                                ? "bg-purple-500/15 border-purple-500/40 border-2 text-purple-300"
                                : "glass-card border border-white/5 hover:border-purple-500/20"
                            }`}
                    >
                        <span className="text-2xl block mb-2">{opt.icon}</span>
                        <span className="text-sm font-medium">{opt.label}</span>
                    </motion.button>
                ))}
            </div>
        </div>
    );

    return (
        <div className="max-w-2xl">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="text-3xl font-bold mb-2">Style Profile</h1>
                <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
                    Help us personalize your outfit recommendations
                </p>

                <SelectionGrid
                    title="What's your gender?"
                    options={GENDERS}
                    selected={gender}
                    onSelect={setGender}
                />

                <SelectionGrid
                    title="What's your body type?"
                    options={BODY_TYPES}
                    selected={bodyType}
                    onSelect={setBodyType}
                />

                <SelectionGrid
                    title="What's your style?"
                    options={STYLES}
                    selected={style}
                    onSelect={setStyle}
                />

                <div className="flex items-center gap-4 mt-6">
                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="btn-primary px-10 py-3 disabled:opacity-50"
                    >
                        {saving ? "Saving..." : saved ? "✓ Saved!" : "Save Profile"}
                    </button>
                    <button
                        onClick={() => router.push("/dashboard")}
                        className="btn-secondary px-8 py-3"
                    >
                        Go to Dashboard
                    </button>
                </div>
            </motion.div>
        </div>
    );
}
