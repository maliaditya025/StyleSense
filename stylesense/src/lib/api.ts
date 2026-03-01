/**
 * Axios API client for StyleSense backend.
 * Provides typed methods for all backend endpoints.
 * Automatically attaches JWT token from localStorage.
 */

import axios from "axios";
import type {
    AuthResponse,
    LoginPayload,
    RegisterPayload,
    ProfileUpdatePayload,
    User,
    Clothing,
    Outfit,
    StylingTips,
    GenerateOutfitsPayload,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Create axios instance with defaults
const api = axios.create({
    baseURL: API_BASE,
    headers: { "Content-Type": "application/json" },
});

// Attach JWT token to every request if available
api.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

// Handle 401 responses (expired/invalid token)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401 && typeof window !== "undefined") {
            localStorage.removeItem("token");
            localStorage.removeItem("user");
            // Redirect to login if not already there
            if (!window.location.pathname.includes("/login")) {
                window.location.href = "/login";
            }
        }
        return Promise.reject(error);
    }
);

// ─── Auth ──────────────────────────────────────────────────────

export async function registerUser(
    payload: RegisterPayload
): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/register", payload);
    return data;
}

export async function loginUser(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>("/login", payload);
    return data;
}

// ─── Profile ───────────────────────────────────────────────────

export async function getProfile(): Promise<User> {
    const { data } = await api.get<User>("/profile");
    return data;
}

export async function updateProfile(
    payload: ProfileUpdatePayload
): Promise<User> {
    const { data } = await api.put<User>("/profile", payload);
    return data;
}

// ─── Clothing ──────────────────────────────────────────────────

export async function uploadClothes(file: File, categoryOverride?: string): Promise<Clothing> {
    const formData = new FormData();
    formData.append("file", file);
    if (categoryOverride) {
        formData.append("category_override", categoryOverride);
    }
    const { data } = await api.post<Clothing>("/upload-clothes", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
}

export async function getCloset(category?: string): Promise<Clothing[]> {
    const params = category ? { category } : {};
    const { data } = await api.get<Clothing[]>("/closet", { params });
    return data;
}

export async function deleteClothing(id: string): Promise<void> {
    await api.delete(`/closet/${id}`);
}

// ─── Outfits ───────────────────────────────────────────────────

export async function generateOutfits(
    payload: GenerateOutfitsPayload
): Promise<Outfit[]> {
    const { data } = await api.post<Outfit[]>("/generate-outfits", payload);
    return data;
}

export async function getStylingTips(outfitId: string): Promise<StylingTips> {
    const { data } = await api.get<StylingTips>("/styling-tips", {
        params: { outfit_id: outfitId },
    });
    return data;
}

export async function getSavedOutfits(): Promise<Outfit[]> {
    const { data } = await api.get<Outfit[]>("/outfits");
    return data;
}

// Helper to get full image URL
export function getImageUrl(path: string): string {
    if (path.startsWith("http")) return path;
    return `${API_BASE}${path}`;
}

export default api;
