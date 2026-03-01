/* ─── TypeScript Types for StyleSense ─────────────────────────── */

export interface User {
  id: string;
  email: string;
  name: string;
  gender?: string | null;
  body_type?: string | null;
  style_preference?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name: string;
}

export interface ProfileUpdatePayload {
  gender?: string;
  body_type?: string;
  style_preference?: string;
  name?: string;
}

export interface Clothing {
  id: string;
  user_id: string;
  category: string;
  confidence_score?: number | null;
  primary_color: string;
  secondary_color?: string | null;
  color_name?: string | null;
  image_url: string;
  created_at?: string;
}

export interface OutfitItem {
  id: string;
  category: string;
  primary_color: string;
  secondary_color?: string | null;
  color_name?: string | null;
  image_url: string;
}

export interface Outfit {
  id: string;
  user_id: string;
  items: OutfitItem[];
  score: number;
  occasion?: string | null;
  tips?: string[] | null;
  created_at?: string;
}

export interface StylingTips {
  outfit_id: string;
  tips: string[];
  accessories: string[];
  footwear: string[];
  dos: string[];
  donts: string[];
  grooming: string[];
}

export interface GenerateOutfitsPayload {
  occasion: string;
}

export type ClothingCategory =
  | "shirt"
  | "t-shirt"
  | "pants"
  | "jeans"
  | "shoes"
  | "jacket"
  | "dress"
  | "accessories"
  | "shorts"
  | "skirt";

export type Occasion = "casual" | "formal" | "party" | "work" | "date";

export type Gender = "male" | "female" | "non-binary";

export type BodyType = "slim" | "athletic" | "average" | "plus-size";

export type StylePreference =
  | "casual"
  | "formal"
  | "streetwear"
  | "bohemian"
  | "minimalist";