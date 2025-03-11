import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { ColorMode, COLORS } from "./colors";

export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

/**
 * Converts a hex color to HSL format for Tailwind CSS variables
 * @param hex Hex color code (e.g. #FFFFFF)
 * @returns HSL values as string (e.g. "0 0% 100%")
 */
export function hexToHsl(hex: string): string {
    // Remove the # symbol if present
    hex = hex.replace(/^#/, '');
    
    // Parse the hex values
    let r = parseInt(hex.slice(0, 2), 16) / 255;
    let g = parseInt(hex.slice(2, 4), 16) / 255;
    let b = parseInt(hex.slice(4, 6), 16) / 255;
    
    // Find the min and max values to calculate the lightness
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    
    // Calculate the lightness
    let l = (max + min) / 2;
    
    let h = 0;
    let s = 0;
    
    if (max !== min) {
        // Calculate the saturation
        s = l > 0.5 ? (max - min) / (2 - max - min) : (max - min) / (max + min);
        
        // Calculate the hue
        if (max === r) {
            h = (g - b) / (max - min) + (g < b ? 6 : 0);
        } else if (max === g) {
            h = (b - r) / (max - min) + 2;
        } else {
            h = (r - g) / (max - min) + 4;
        }
        
        h *= 60;
    }
    
    // Round values
    h = Math.round(h);
    s = Math.round(s * 100);
    l = Math.round(l * 100);
    
    return `${h} ${s}% ${l}%`;
}

/**
 * Gets the HSL values for the current theme to use with Tailwind CSS
 * @param mode The color mode
 * @returns An object with HSL values for each color
 */
export function getThemeHslValues(mode: ColorMode) {
    const colors = COLORS[mode as keyof typeof COLORS];
    
    return {
        primary: hexToHsl(colors.primary_02),
        primaryForeground: hexToHsl(colors.neutral_13),
        secondary: hexToHsl(colors.secondary_01),
        secondaryForeground: hexToHsl(colors.primary_01),
        accent: hexToHsl(colors.accent_01),
        accentForeground: hexToHsl(colors.primary_01),
        background: hexToHsl(colors.neutral_13),
        foreground: hexToHsl(colors.primary_01),
        card: hexToHsl(colors.neutral_12),
        cardForeground: hexToHsl(colors.primary_01),
        popover: hexToHsl(colors.neutral_13),
        popoverForeground: hexToHsl(colors.primary_01),
        muted: hexToHsl(colors.secondary_02),
        mutedForeground: hexToHsl(colors.neutral_08),
        border: hexToHsl(colors.neutral_10),
        input: hexToHsl(colors.neutral_10),
        ring: hexToHsl(colors.primary_03)
    };
}