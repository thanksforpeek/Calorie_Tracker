import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedTheme = localStorage.getItem("theme");
        return savedTheme ? savedTheme === "dark" : false;
    });

    useEffect(() => {
        const theme = isDarkMode ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("theme", theme);
    }, [isDarkMode]);

    const toggleTheme = () => setIsDarkMode((prev) => !prev);

    return (
        <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
            {children}
        </ThemeContext.Provider>
    );
}

export const useTheme = () => useContext(ThemeContext);