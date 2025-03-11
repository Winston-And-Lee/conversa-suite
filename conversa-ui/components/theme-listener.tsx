"use client";

import { useEffect } from "react";
import { useTheme, THEME_STORAGE_KEY } from "@/lib/theme-provider";
import { ColorMode } from "@/lib/colors";

export function ThemeListener() {
  const { setMode } = useTheme();

  useEffect(() => {
    // Function to handle storage events
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === THEME_STORAGE_KEY && event.newValue) {
        setMode(event.newValue as ColorMode);
      }
    };

    // Add event listener
    window.addEventListener("storage", handleStorageChange);

    // Clean up
    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [setMode]);

  // This component doesn't render anything
  return null;
} 