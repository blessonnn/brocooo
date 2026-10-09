/**
 * Brocooo Caption Style Types
 *
 * This is the canonical type definition for caption styles.
 * Used by both the frontend (canvas preview) and backend (ASS generation).
 */

export interface CaptionFont {
  family: string;
  size: number;
  weight: number;
  italic: boolean;
  uppercase: boolean;
  letterSpacing: number;
}

export interface CaptionColors {
  fill: string;
  stroke: string;
  strokeWidth: number;
  shadow?: string;
  activeWord: string;
  activeBg?: string;
}

export interface CaptionBackground {
  enabled: boolean;
  color: string;
  opacity: number;
  borderRadius: number;
  padding: [number, number, number, number];
}

export interface CaptionPosition {
  vertical: "top" | "center" | "bottom";
  marginBottom: number;
  alignment: "left" | "center" | "right";
}

export interface CaptionDisplay {
  wordsPerLine: number;
  maxLines: number;
  mode: "phrase" | "word" | "sentence";
}

export type AnimationType =
  | "none"
  | "pop"
  | "bounce"
  | "karaoke-sweep"
  | "typewriter"
  | "fade"
  | "scale-up"
  | "glitch"
  | "wave";

export interface CaptionAnimation {
  type: AnimationType;
  activeWordScale: number;
  duration: number; // ms
  easing: string;
}

export interface CaptionEmoji {
  enabled: boolean;
  position: "inline" | "above" | "below";
  reactiveToSentiment: boolean;
}

export type CaptionCategory =
  | "bold"
  | "minimal"
  | "animated"
  | "retro"
  | "cinematic"
  | "fun";

export interface CaptionStyle {
  id: string;
  name: string;
  category: CaptionCategory;
  font: CaptionFont;
  colors: CaptionColors;
  background: CaptionBackground;
  position: CaptionPosition;
  display: CaptionDisplay;
  animation: CaptionAnimation;
  emoji: CaptionEmoji;
}

/** Default values for partial style creation */
export const DEFAULT_CAPTION_STYLE: CaptionStyle = {
  id: "custom",
  name: "Custom",
  category: "bold",
  font: {
    family: "Montserrat",
    size: 56,
    weight: 800,
    italic: false,
    uppercase: true,
    letterSpacing: 0,
  },
  colors: {
    fill: "#FFFFFF",
    stroke: "#000000",
    strokeWidth: 4,
    activeWord: "#FFD700",
  },
  background: {
    enabled: false,
    color: "#000000",
    opacity: 0.7,
    borderRadius: 8,
    padding: [8, 16, 8, 16],
  },
  position: {
    vertical: "bottom",
    marginBottom: 120,
    alignment: "center",
  },
  display: {
    wordsPerLine: 4,
    maxLines: 2,
    mode: "phrase",
  },
  animation: {
    type: "pop",
    activeWordScale: 1.15,
    duration: 150,
    easing: "ease-out",
  },
  emoji: {
    enabled: false,
    position: "inline",
    reactiveToSentiment: false,
  },
};
