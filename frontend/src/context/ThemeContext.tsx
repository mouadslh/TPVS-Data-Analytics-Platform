import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { ConfigProvider, theme } from 'antd';
import frFR from 'antd/locale/fr_FR';

interface ThemeContextType {
  dark: boolean;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextType>({ dark: false, toggle: () => {} });

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [dark, setDark] = useState(localStorage.getItem('tpvs_dark') === 'true');

  useEffect(() => {
    localStorage.setItem('tpvs_dark', String(dark));
    document.body.setAttribute('data-theme', dark ? 'dark' : 'light');
  }, [dark]);

  const toggle = () => setDark((d) => !d);

  return (
    <ThemeContext.Provider value={{ dark, toggle }}>
      <ConfigProvider
        locale={frFR}
        theme={{ algorithm: dark ? theme.darkAlgorithm : theme.defaultAlgorithm }}
      >
        {children}
      </ConfigProvider>
    </ThemeContext.Provider>
  );
}

export const useTheme = () => useContext(ThemeContext);
