"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { loginUser } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    const { login } = useAuthStore();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            const res = await loginUser({ email, password });
            login(res.user, res.access_token);
            router.push("/dashboard");
        } catch (err: any) {
            setError(err.response?.data?.detail || "Login failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-strong p-8 rounded-2xl">
            {/* Logo */}
            <div className="text-center mb-8">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center mx-auto mb-4">
                    <span className="text-white font-bold text-2xl">S</span>
                </div>
                <h1 className="text-2xl font-bold mb-1">Welcome Back</h1>
                <p style={{ color: "var(--text-secondary)" }}>Sign in to StyleSense</p>
            </div>

            {/* Error message */}
            {error && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center"
                >
                    {error}
                </motion.div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                        Email Address
                    </label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="input-field"
                        placeholder="you@example.com"
                        required
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                        Password
                    </label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="input-field"
                        placeholder="••••••••"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full py-4 rounded-xl text-base mt-6 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {loading ? (
                        <span className="flex items-center justify-center gap-2">
                            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Signing in...
                        </span>
                    ) : (
                        "Sign In"
                    )}
                </button>
            </form>

            <p className="text-center mt-6 text-sm" style={{ color: "var(--text-secondary)" }}>
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-purple-400 hover:text-purple-300 font-medium transition-colors">
                    Create one
                </Link>
            </p>
        </div>
    );
}
