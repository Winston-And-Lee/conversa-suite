"use client";

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { COLORS, ColorMode } from './colors';
import { getThemeHslValues } from './utils';

export const THEME_STORAGE_KEY = 'app-theme';

interface ThemeContextType {
  mode: ColorMode;
  setMode: (theme: ColorMode) => void;
  colors: typeof COLORS.default;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider = ({ children }: ThemeProviderProps) => {
  const [mode, setMode] = useState<ColorMode>('default');
  const [colors, setColors] = useState(COLORS.default);

  // Load theme from local storage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ColorMode;
      if (savedTheme && COLORS[savedTheme as keyof typeof COLORS]) {
        setMode(savedTheme);
        setColors(COLORS[savedTheme as keyof typeof COLORS]);
      } else {
        localStorage.setItem(THEME_STORAGE_KEY, 'default');
      }
    }
  }, []);

  // Update theme and local storage
  const handleSetMode = (newTheme: ColorMode) => {
    setMode(newTheme);
    setColors(COLORS[newTheme as keyof typeof COLORS]);
    if (typeof window !== 'undefined') {
      localStorage.setItem(THEME_STORAGE_KEY, newTheme);
    }
  };

  // Set CSS variables for the theme
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const root = document.documentElement;
      
      // Set direct CSS properties for components that use raw CSS
      root.style.setProperty('--primary-01', colors.primary_01);
      root.style.setProperty('--primary-02', colors.primary_02);
      root.style.setProperty('--primary-03', colors.primary_03);
      root.style.setProperty('--primary-04', colors.primary_04);
      root.style.setProperty('--primary-05', colors.primary_05);
      
      root.style.setProperty('--secondary-01', colors.secondary_01);
      root.style.setProperty('--secondary-02', colors.secondary_02);
      
      root.style.setProperty('--accent-01', colors.accent_01);
      root.style.setProperty('--accent-02', colors.accent_02);
      
      root.style.setProperty('--neutral-07', colors.neutral_07);
      root.style.setProperty('--neutral-08', colors.neutral_08);
      root.style.setProperty('--neutral-10', colors.neutral_10);
      root.style.setProperty('--neutral-12', colors.neutral_12);
      root.style.setProperty('--neutral-13', colors.neutral_13);
      
      // Set Tailwind CSS HSL variables
      const hslValues = getThemeHslValues(mode);
      
      root.style.setProperty('--primary', hslValues.primary);
      root.style.setProperty('--primary-foreground', hslValues.primaryForeground);
      
      root.style.setProperty('--secondary', hslValues.secondary);
      root.style.setProperty('--secondary-foreground', hslValues.secondaryForeground);
      
      root.style.setProperty('--accent', hslValues.accent);
      root.style.setProperty('--accent-foreground', hslValues.accentForeground);
      
      root.style.setProperty('--background', hslValues.background);
      root.style.setProperty('--foreground', hslValues.foreground);
      
      root.style.setProperty('--card', hslValues.card);
      root.style.setProperty('--card-foreground', hslValues.cardForeground);
      
      root.style.setProperty('--popover', hslValues.popover);
      root.style.setProperty('--popover-foreground', hslValues.popoverForeground);
      
      root.style.setProperty('--muted', hslValues.muted);
      root.style.setProperty('--muted-foreground', hslValues.mutedForeground);
      
      root.style.setProperty('--destructive', '0 84.2% 60.2%'); // Keep the original destructive color
      root.style.setProperty('--destructive-foreground', '0 0% 98%');
      
      root.style.setProperty('--border', hslValues.border);
      root.style.setProperty('--input', hslValues.input);
      root.style.setProperty('--ring', hslValues.ring);
    }
  }, [colors, mode]);

  const themeContextValue: ThemeContextType = {
    mode,
    setMode: handleSetMode,
    colors
  };

  return (
    <ThemeContext.Provider value={themeContextValue}>
      {children}
    </ThemeContext.Provider>
  );
}; 