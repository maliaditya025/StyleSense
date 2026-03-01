"use client";

import { useState, useRef, Suspense } from "react";
import { motion } from "framer-motion";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

// Simple mannequin body parts as colored geometries
function Mannequin({ topColor, bottomColor, shoeColor }: {
    topColor: string;
    bottomColor: string;
    shoeColor: string;
}) {
    const groupRef = useRef<THREE.Group>(null);

    useFrame((state) => {
        if (groupRef.current) {
            groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
        }
    });

    return (
        <group ref={groupRef} position={[0, -1.5, 0]}>
            {/* Head */}
            <mesh position={[0, 3.6, 0]}>
                <sphereGeometry args={[0.35, 32, 32]} />
                <meshStandardMaterial color="#e8d5c4" roughness={0.6} />
            </mesh>

            {/* Neck */}
            <mesh position={[0, 3.15, 0]}>
                <cylinderGeometry args={[0.12, 0.15, 0.3, 16]} />
                <meshStandardMaterial color="#e8d5c4" roughness={0.6} />
            </mesh>

            {/* Torso (top clothing) */}
            <mesh position={[0, 2.4, 0]}>
                <boxGeometry args={[1.0, 1.2, 0.5]} />
                <meshStandardMaterial color={topColor} roughness={0.4} metalness={0.1} />
            </mesh>

            {/* Left arm */}
            <mesh position={[-0.65, 2.4, 0]} rotation={[0, 0, 0.15]}>
                <boxGeometry args={[0.25, 1.1, 0.25]} />
                <meshStandardMaterial color={topColor} roughness={0.4} metalness={0.1} />
            </mesh>

            {/* Right arm */}
            <mesh position={[0.65, 2.4, 0]} rotation={[0, 0, -0.15]}>
                <boxGeometry args={[0.25, 1.1, 0.25]} />
                <meshStandardMaterial color={topColor} roughness={0.4} metalness={0.1} />
            </mesh>

            {/* Left hand */}
            <mesh position={[-0.75, 1.75, 0]}>
                <sphereGeometry args={[0.12, 16, 16]} />
                <meshStandardMaterial color="#e8d5c4" roughness={0.6} />
            </mesh>

            {/* Right hand */}
            <mesh position={[0.75, 1.75, 0]}>
                <sphereGeometry args={[0.12, 16, 16]} />
                <meshStandardMaterial color="#e8d5c4" roughness={0.6} />
            </mesh>

            {/* Belt/waist */}
            <mesh position={[0, 1.75, 0]}>
                <boxGeometry args={[1.02, 0.1, 0.52]} />
                <meshStandardMaterial color="#2a2a2a" roughness={0.3} metalness={0.3} />
            </mesh>

            {/* Left leg (bottom clothing) */}
            <mesh position={[-0.25, 0.85, 0]}>
                <boxGeometry args={[0.4, 1.7, 0.4]} />
                <meshStandardMaterial color={bottomColor} roughness={0.4} metalness={0.1} />
            </mesh>

            {/* Right leg (bottom clothing) */}
            <mesh position={[0.25, 0.85, 0]}>
                <boxGeometry args={[0.4, 1.7, 0.4]} />
                <meshStandardMaterial color={bottomColor} roughness={0.4} metalness={0.1} />
            </mesh>

            {/* Left shoe */}
            <mesh position={[-0.25, -0.1, 0.08]}>
                <boxGeometry args={[0.38, 0.2, 0.55]} />
                <meshStandardMaterial color={shoeColor} roughness={0.3} metalness={0.2} />
            </mesh>

            {/* Right shoe */}
            <mesh position={[0.25, -0.1, 0.08]}>
                <boxGeometry args={[0.38, 0.2, 0.55]} />
                <meshStandardMaterial color={shoeColor} roughness={0.3} metalness={0.2} />
            </mesh>
        </group>
    );
}

// Floor/platform
function Platform() {
    return (
        <mesh position={[0, -1.7, 0]} rotation={[-Math.PI / 2, 0, 0]}>
            <circleGeometry args={[1.5, 64]} />
            <meshStandardMaterial color="#1a1a2e" roughness={0.2} metalness={0.8} />
        </mesh>
    );
}

// Lighting setup
function Lighting() {
    return (
        <>
            <ambientLight intensity={0.4} />
            <directionalLight position={[5, 5, 5]} intensity={0.8} castShadow />
            <directionalLight position={[-3, 3, -3]} intensity={0.3} />
            <pointLight position={[0, 5, 0]} intensity={0.5} color="#a855f7" />
            <pointLight position={[3, 2, 2]} intensity={0.3} color="#3b82f6" />
        </>
    );
}

export default function TryOnPage() {
    const [topColor, setTopColor] = useState("#2563eb");
    const [bottomColor, setBottomColor] = useState("#1e3a5f");
    const [shoeColor, setShoeColor] = useState("#1a1a1a");

    const presetOutfits = [
        { name: "Classic Blue", top: "#2563eb", bottom: "#1e3a5f", shoes: "#1a1a1a" },
        { name: "Warm Earth", top: "#b45309", bottom: "#78350f", shoes: "#44403c" },
        { name: "Night Out", top: "#0f172a", bottom: "#0f172a", shoes: "#1a1a1a" },
        { name: "Summer Vibes", top: "#f97316", bottom: "#f5f5f4", shoes: "#d4d4d4" },
        { name: "Forest Green", top: "#166534", bottom: "#1e293b", shoes: "#292524" },
        { name: "Purple Reign", top: "#7c3aed", bottom: "#0f172a", shoes: "#1a1a1a" },
    ];

    return (
        <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h1 className="text-3xl font-bold mb-2">3D Try-On</h1>
                <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
                    Preview outfit combinations on a 3D mannequin • Drag to rotate, scroll to zoom
                </p>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* 3D Viewer */}
                    <div className="lg:col-span-2 glass-card overflow-hidden" style={{ height: "500px" }}>
                        <Canvas camera={{ position: [0, 0.5, 4.5], fov: 45 }} shadows>
                            <Suspense fallback={null}>
                                <Lighting />
                                <Mannequin topColor={topColor} bottomColor={bottomColor} shoeColor={shoeColor} />
                                <Platform />
                                <OrbitControls
                                    enablePan={false}
                                    minDistance={3}
                                    maxDistance={8}
                                    minPolarAngle={Math.PI / 6}
                                    maxPolarAngle={Math.PI / 1.5}
                                />
                            </Suspense>
                        </Canvas>
                    </div>

                    {/* Controls */}
                    <div className="space-y-6">
                        {/* Color Pickers */}
                        <div className="glass-card p-5">
                            <h3 className="text-sm font-semibold mb-4">🎨 Customize Colors</h3>

                            <div className="space-y-4">
                                <div>
                                    <label className="text-xs mb-2 block" style={{ color: "var(--text-secondary)" }}>Top</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={topColor}
                                            onChange={(e) => setTopColor(e.target.value)}
                                            className="w-10 h-10 rounded-lg cursor-pointer border-0 bg-transparent"
                                        />
                                        <span className="text-sm font-mono" style={{ color: "var(--text-secondary)" }}>{topColor}</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs mb-2 block" style={{ color: "var(--text-secondary)" }}>Bottom</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={bottomColor}
                                            onChange={(e) => setBottomColor(e.target.value)}
                                            className="w-10 h-10 rounded-lg cursor-pointer border-0 bg-transparent"
                                        />
                                        <span className="text-sm font-mono" style={{ color: "var(--text-secondary)" }}>{bottomColor}</span>
                                    </div>
                                </div>

                                <div>
                                    <label className="text-xs mb-2 block" style={{ color: "var(--text-secondary)" }}>Shoes</label>
                                    <div className="flex items-center gap-3">
                                        <input
                                            type="color"
                                            value={shoeColor}
                                            onChange={(e) => setShoeColor(e.target.value)}
                                            className="w-10 h-10 rounded-lg cursor-pointer border-0 bg-transparent"
                                        />
                                        <span className="text-sm font-mono" style={{ color: "var(--text-secondary)" }}>{shoeColor}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Preset Outfits */}
                        <div className="glass-card p-5">
                            <h3 className="text-sm font-semibold mb-4">👔 Preset Outfits</h3>
                            <div className="grid grid-cols-2 gap-2">
                                {presetOutfits.map((preset) => (
                                    <button
                                        key={preset.name}
                                        onClick={() => {
                                            setTopColor(preset.top);
                                            setBottomColor(preset.bottom);
                                            setShoeColor(preset.shoes);
                                        }}
                                        className="p-3 rounded-xl text-left glass-card hover:border-purple-500/30 transition-all"
                                    >
                                        <div className="flex gap-1 mb-2">
                                            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: preset.top }} />
                                            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: preset.bottom }} />
                                            <div className="w-5 h-5 rounded-full" style={{ backgroundColor: preset.shoes }} />
                                        </div>
                                        <p className="text-xs font-medium">{preset.name}</p>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Instructions */}
                        <div className="glass-card p-5">
                            <h3 className="text-sm font-semibold mb-3">🎮 Controls</h3>
                            <ul className="space-y-2 text-xs" style={{ color: "var(--text-secondary)" }}>
                                <li>🖱️ Left-click + drag to rotate</li>
                                <li>📜 Scroll to zoom in/out</li>
                                <li>🎨 Pick colors or use presets</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
