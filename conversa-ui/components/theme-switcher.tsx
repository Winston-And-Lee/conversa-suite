"use client";

import { useState, useEffect } from "react";
import { useTheme } from "@/lib/theme-provider";
import { ColorMode } from "@/lib/colors";
import { cn } from "@/lib/utils";

// Mapping of color modes to display names and color indicators
const themeOptions: { value: ColorMode, label: string, color: string }[] = [
  { value: "default", label: "Default", color: "#21645A" },
  { value: "secondary", label: "Secondary", color: "#00F" },
  { value: "green", label: "Green", color: "#73D13D" },
  { value: "blue", label: "Blue", color: "#597EF7" },
  { value: "pink", label: "Pink", color: "#F759AB" },
  { value: "red", label: "Red", color: "#FF7875" },
  { value: "orange", label: "Orange", color: "#FFA940" },
  { value: "lightBlue", label: "Light Blue", color: "#40A9FF" },
  { value: "yellow", label: "Yellow", color: "#FFEC3D" }
];

export function ThemeSwitcher() {
  const { mode, setMode } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  // Prevent hydration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setIsOpen(false);
    };

    if (isOpen) {
      document.addEventListener("click", handleClickOutside);
    }

    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [isOpen]);

  if (!mounted) {
    return null;
  }

  const currentTheme = themeOptions.find(option => option.value === mode) || themeOptions[0];

  return (
    <div className="relative">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="flex items-center gap-2 px-3 py-2 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <span 
          className="w-5 h-5 rounded-full" 
          style={{ backgroundColor: currentTheme.color }}
        />
        <span className="font-medium">{currentTheme.label}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-popover shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
          <div className="py-2">
            {themeOptions.map((option) => (
              <button
                key={option.value}
                onClick={(e) => {
                  e.stopPropagation();
                  setMode(option.value);
                  setIsOpen(false);
                }}
                className={cn(
                  "flex items-center gap-3 w-full px-4 py-2.5 text-left text-sm hover:bg-accent hover:text-accent-foreground",
                  mode === option.value && "bg-muted font-medium"
                )}
              >
                <span 
                  className="w-5 h-5 rounded-full" 
                  style={{ backgroundColor: option.color }}
                />
                <span>{option.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 