import { useThemeContext } from '@/contexts/color-mode';

export const ThemeSwitcher = () => {
  const { setMode, mode } = useThemeContext();

  const switchToDefault = () => setMode('default');
  const switchToSecondary = () => setMode('secondary');

  return (
    <div>
      <p>Current Theme: {mode}</p>
      <button onClick={switchToDefault}>Default Theme</button>
      <button onClick={switchToSecondary}>Secondary Theme</button>
    </div>
  );
};
