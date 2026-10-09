import hormozi from "./hormozi.json";
import mrbeast from "./mrbeast.json";
import karaokeSweep from "./karaoke-sweep.json";
import neonGlow from "./neon-glow.json";
import minimalClean from "./minimal-clean.json";
import { CaptionStyle } from "../types";

export const PRESETS: Record<string, CaptionStyle> = {
  hormozi: hormozi as CaptionStyle,
  mrbeast: mrbeast as CaptionStyle,
  "karaoke-sweep": karaokeSweep as CaptionStyle,
  "neon-glow": neonGlow as CaptionStyle,
  "minimal-clean": minimalClean as CaptionStyle,
};

export const PRESET_LIST: CaptionStyle[] = Object.values(PRESETS);

export * from "../types";
