"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import QRCodeComponent from "@/components/shared/QRCode";

export default function QRCodePage() {
    const [url, setUrl] = useState("");

    useEffect(() => {
        // Get the current domain and build the login URL
        if (typeof window !== "undefined") {
            const protocol = window.location.protocol;
            const host = window.location.host;
            const baseUrl = `${protocol}//${host}`;
            setUrl(`${baseUrl}/login`);
        }
    }, []);

    return (
        <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-3xl font-bold mb-2">Quick Access</h1>
                <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
                    Share this QR code to get instant access to StyleSense
                </p>

                {url && <QRCodeComponent value={url} subtitle="Scan with any QR code reader to access StyleSense" />}

                {/* Additional Info */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mt-8 max-w-md mx-auto"
                >
                    <div className="glass-card p-6 rounded-xl">
                        <h3 className="font-bold mb-3">How to use:</h3>
                        <ol className="text-sm space-y-2" style={{ color: "var(--text-secondary)" }}>
                            <li>1. Open any QR code reader app</li>
                            <li>2. Point your camera at the QR code</li>
                            <li>3. Tap the link to access StyleSense</li>
                            <li>4. Login or create an account</li>
                        </ol>
                    </div>
                </motion.div>

                {/* Share Info */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="mt-6 max-w-md mx-auto"
                >
                    <div className="glass-card p-6 rounded-xl border border-purple-500/20">
                        <h3 className="font-bold mb-2">💡 Pro Tip:</h3>
                        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                            Download the QR code and print it on posters, business cards, or share it on social media to direct people to StyleSense!
                        </p>
                    </div>
                </motion.div>
            </motion.div>
        </div>
    );
}
