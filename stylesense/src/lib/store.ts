/**
 * Zustand state management stores for StyleSense.
 * Handles auth state, closet data, and outfit recommendations.
 */

"use client";

import { create } from "zustand";
import type { User, Clothing, Outfit } from "./types";

// ─── Auth Store ────────────────────────────────────────────────

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    login: (user: User, token: string) => void;
    logout: () => void;
    updateUser: (user: Partial<User>) => void;
    hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    token: null,
    isAuthenticated: false,

    login: (user, token) => {
        if (typeof window !== "undefined") {
            localStorage.setItem("token", token);
            localStorage.setItem("user", JSON.stringify(user));
        }
        set({ user, token, isAuthenticated: true });
    },

    logout: () => {
        if (typeof window !== "undefined") {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
        }
        set({ user: null, token: null, isAuthenticated: false });
    },

    updateUser: (updates) => {
        const currentUser = get().user;
        if (currentUser) {
            const updated = { ...currentUser, ...updates };
            if (typeof window !== "undefined") {
                localStorage.setItem("user", JSON.stringify(updated));
            }
            set({ user: updated });
        }
    },

    hydrate: () => {
        if (typeof window !== "undefined") {
            const token = localStorage.getItem("token");
            const userStr = localStorage.getItem("user");
            if (token && userStr) {
                try {
                    const user = JSON.parse(userStr) as User;
                    set({ user, token, isAuthenticated: true });
                } catch {
                    set({ user: null, token: null, isAuthenticated: false });
                }
            }
        }
    },
}));

// ─── Closet Store ──────────────────────────────────────────────

interface ClosetState {
    clothes: Clothing[];
    isLoading: boolean;
    setClothes: (clothes: Clothing[]) => void;
    addItem: (item: Clothing) => void;
    removeItem: (id: string) => void;
    setLoading: (loading: boolean) => void;
}

export const useClosetStore = create<ClosetState>((set, get) => ({
    clothes: [],
    isLoading: false,

    setClothes: (clothes) => set({ clothes }),
    addItem: (item) => set({ clothes: [item, ...get().clothes] }),
    removeItem: (id) =>
        set({ clothes: get().clothes.filter((c) => c.id !== id) }),
    setLoading: (loading) => set({ isLoading: loading }),
}));

// ─── Outfits Store ─────────────────────────────────────────────

interface OutfitState {
    outfits: Outfit[];
    isLoading: boolean;
    selectedOccasion: string;
    setOutfits: (outfits: Outfit[]) => void;
    setLoading: (loading: boolean) => void;
    setOccasion: (occasion: string) => void;
}

export const useOutfitStore = create<OutfitState>((set) => ({
    outfits: [],
    isLoading: false,
    selectedOccasion: "casual",

    setOutfits: (outfits) => set({ outfits }),
    setLoading: (loading) => set({ isLoading: loading }),
    setOccasion: (occasion) => set({ selectedOccasion: occasion }),
}));
