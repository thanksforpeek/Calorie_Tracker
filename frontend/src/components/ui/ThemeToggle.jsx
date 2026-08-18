import { useTheme } from "../../context/ThemeContext";
import "./ThemeToggle.css";

function ThemeToggle() {
    const { isDarkMode, toggleTheme } = useTheme();

    return (
        <button className="theme-toggle-btn" onClick={toggleTheme} title="Toggle Theme">
            {isDarkMode ? "☀️ Light" : "🌙 Dark"}
        </button>
    );
}

export default ThemeToggle;