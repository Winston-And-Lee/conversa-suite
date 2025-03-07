import React, { createContext, PropsWithChildren, useContext, useEffect, useState } from 'react';

import { ColorMode, COLORS, FONT_STYLE } from '@/constant';
import { getThemeColorNameByEnum } from '@/utils';
import { ConfigProvider } from 'antd';
import { ThemeProvider } from 'styled-components';

export const THEME_STORAGE_KEY = 'app-theme';

interface ThemeContextType {
  mode: ColorMode;
  setMode: (theme: ColorMode) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useThemeContext = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useThemeContext must be used within a ThemeProvider');
  }
  return context;
};

export const KhaojaiThemeProvider: React.FC<PropsWithChildren> = ({ children }) => {
  // const userProfile = JSON.parse(localStorage.getItem(USER_KEY) || '{}');
  const appTheme = localStorage.getItem(THEME_STORAGE_KEY) as ColorMode;
  const themeName = getThemeColorNameByEnum(appTheme ?? 'default');

  const [mode, setMode] = useState<ColorMode>(themeName as ColorMode);
  const [theme, setColor] = useState({ colors: COLORS[themeName as keyof typeof COLORS] });

  // Load theme from local storage on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as ColorMode;
    if (savedTheme && COLORS[savedTheme as keyof typeof COLORS]) {
      setMode(themeName);
      setColor({ colors: COLORS[savedTheme as keyof typeof COLORS] });
    } else {
      localStorage.setItem(THEME_STORAGE_KEY, themeName);
    }
  }, []);

  // Update theme and local storage
  const handleSetMode = (newTheme: ColorMode) => {
    setMode(newTheme); // Update mode immediately
    setColor({ colors: COLORS[newTheme as keyof typeof COLORS] }); // Update color directly
    localStorage.setItem(THEME_STORAGE_KEY, newTheme); // Persist to localStorage
  };

  const themeContextValue = {
    mode,
    setMode: handleSetMode
  };

  return (
    <ThemeContext.Provider value={themeContextValue}>
      <ThemeProvider theme={theme}>
        <ConfigProvider
          theme={{
            hashed: false,
            token: {
              fontFamily: 'IBM Plex Sans Thai',
              colorPrimary: theme.colors.primary_02,
              colorPrimaryActive: theme.colors.primary_01,
              colorPrimaryHover: theme.colors.primary_03,
              fontWeightStrong: 500
            },
            components: {
              Typography: {
                fontFamily: 'IBM Plex Sans Thai',
                titleMarginBottom: 0
              },
              Table: {
                borderColor: 'var(--neutral_10)',
                headerSplitColor: 'var(--neutral_10)'
              },
              Timeline: {
                tailColor: 'var(--neutral_08)',
                tailWidth: 1
              },
              Button: {
                ...FONT_STYLE['Button text/16']
              },
              Form: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt'],
                itemMarginBottom: 22
              },
              Input: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt'],
                inputFontSize: 14
              },
              Segmented: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt'],
                itemActiveBg: '#00A9BE',
                itemSelectedBg: '#00A9BE',
                itemSelectedColor: '#FFFFFF',
                trackBg: '#EEFCFF'
              },
              Checkbox: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt']
              },
              DatePicker: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt']
              },
              Steps: {
                ...FONT_STYLE['Body - 14/Body - Regular -14pt']
              },
              Divider: {
                colorSplit: 'rgba(5, 5, 5, 0.06)'
              }
            }
          }}
        >
          {children}
        </ConfigProvider>
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};
