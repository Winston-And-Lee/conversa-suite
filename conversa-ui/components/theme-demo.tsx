"use client";

import { useTheme } from "@/lib/theme-provider";
import { ThemeSwitcher } from "./theme-switcher";

export function ThemeDemo() {
  const { colors } = useTheme();

  return (
    <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6 space-y-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Theme Demo</h1>
        <div className="px-2">
          <ThemeSwitcher />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* Primary Colors */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b pb-2">Primary Colors</h2>
          <div className="grid grid-cols-1 gap-3">
            <ColorBlock color={colors.primary_01} name="Primary 01" />
            <ColorBlock color={colors.primary_02} name="Primary 02" />
            <ColorBlock color={colors.primary_03} name="Primary 03" />
            <ColorBlock color={colors.primary_04} name="Primary 04" />
            <ColorBlock color={colors.primary_05} name="Primary 05" />
          </div>
        </div>

        {/* Secondary and Accent Colors */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b pb-2">Secondary & Accent Colors</h2>
          <div className="grid grid-cols-1 gap-3">
            <ColorBlock color={colors.secondary_01} name="Secondary 01" />
            <ColorBlock color={colors.secondary_02} name="Secondary 02" />
            <ColorBlock color={colors.accent_01} name="Accent 01" />
            <ColorBlock color={colors.accent_02} name="Accent 02" />
          </div>
        </div>

        {/* Neutral Colors */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b pb-2">Neutral Colors</h2>
          <div className="grid grid-cols-1 gap-3">
            <ColorBlock color={colors.neutral_07} name="Neutral 07" />
            <ColorBlock color={colors.neutral_08} name="Neutral 08" />
            <ColorBlock color={colors.neutral_10} name="Neutral 10" />
            <ColorBlock color={colors.neutral_12} name="Neutral 12" />
            <ColorBlock color={colors.neutral_13} name="Neutral 13" textDark={true} />
          </div>
        </div>

        {/* Theme Showcase */}
        <div className="space-y-6">
          <h2 className="text-2xl font-semibold border-b pb-2">UI Examples</h2>
          <div className="space-y-5">
            <div className="p-5 bg-card rounded-lg shadow border">
              <h3 className="font-medium mb-3">Card Component</h3>
              <p className="text-muted-foreground">This is a card with the current theme</p>
            </div>
            
            <div className="p-5 bg-primary text-primary-foreground rounded-lg">
              <h3 className="font-medium mb-3">Primary Element</h3>
              <p>Primary background with primary foreground text</p>
            </div>
            
            <div className="p-5 bg-secondary text-secondary-foreground rounded-lg">
              <h3 className="font-medium mb-3">Secondary Element</h3>
              <p>Secondary background with secondary foreground text</p>
            </div>
            
            <div className="p-5 bg-accent text-accent-foreground rounded-lg">
              <h3 className="font-medium mb-3">Accent Element</h3>
              <p>Accent background with accent foreground text</p>
            </div>
            
            <div className="p-5 bg-muted rounded-lg">
              <h3 className="font-medium mb-3">Muted Element</h3>
              <p className="text-muted-foreground">Muted background with muted foreground text</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ColorBlock({ color, name, textDark = false }: { color: string; name: string; textDark?: boolean }) {
  return (
    <div
      className="flex items-center justify-between p-4 rounded-md"
      style={{ backgroundColor: color, color: textDark ? "#1D443E" : "#FFFFFF" }}
    >
      <span className="font-medium">{name}</span>
      <span>{color}</span>
    </div>
  );
} 