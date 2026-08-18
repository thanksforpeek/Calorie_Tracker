import { ThemeProvider } from "./context/ThemeContext";
import HomePage from './pages/home/index.jsx'

function App() {
    return (
        <ThemeProvider>
            <HomePage />
        </ThemeProvider>
    );
}

export default App