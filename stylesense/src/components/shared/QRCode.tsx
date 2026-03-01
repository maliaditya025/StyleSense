import { useRef } from "react";
import { QRCodeSVG } from "qrcode.react";
import { motion } from "framer-motion";

interface QRCodeProps {
    value: string;
    title?: string;
    subtitle?: string;
    downloadable?: boolean;
}

export default function QRCodeComponent({ value, title = "StyleSense Access", subtitle, downloadable = true }: QRCodeProps) {
    const qrRef = useRef<any>(null);

    const handleDownload = () => {
        if (qrRef.current) {
            const canvas = qrRef.current.querySelector("canvas");
            const url = canvas.toDataURL("image/png");
            const link = document.createElement("a");
            link.href = url;
            link.download = "stylesense-qr.png";
            link.click();
        }
    };

    const handleCopy = () => {
        navigator.clipboard.writeText(value);
        alert("URL copied to clipboard!");
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-md mx-auto text-center"
        >
            <div className="glass-strong p-8 rounded-2xl">
                {title && <h2 className="text-xl font-bold mb-2">{title}</h2>}
                {subtitle && <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>{subtitle}</p>}

                <div ref={qrRef} className="flex justify-center mb-6 p-4 bg-white rounded-xl">
                    <QRCodeSVG
                        value={value}
                        size={256}
                        level="H"
                        includeMargin={true}
                        fgColor="#000000"
                        bgColor="#ffffff"
                    />
                </div>

                <div className="space-y-3">
                    {downloadable && (
                        <button
                            onClick={handleDownload}
                            className="btn-primary w-full py-2 px-4 rounded-lg"
                        >
                            📥 Download QR Code
                        </button>
                    )}
                    <button
                        onClick={handleCopy}
                        className="btn-secondary w-full py-2 px-4 rounded-lg"
                    >
                        🔗 Copy URL
                    </button>
                </div>

                <p className="text-xs mt-4 p-3 rounded-lg bg-white/5" style={{ color: "var(--text-muted)" }}>
                    <strong>URL:</strong> <br /> {value}
                </p>
            </div>
        </motion.div>
    );
}
