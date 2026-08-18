import { useState } from "react";
import "./Auth.css";
import ThemeToggle from "../ui/ThemeToggle";
import { API_BASE_URL } from '../../utils/config';

function Auth({ onLoginSuccess }) {
    const [isRegister, setIsRegister] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        const endpoint = isRegister ? "/api/auth/register" : "/api/auth/login";

        try {
            console.log("ОТПРАВКА НА:", API_BASE_URL);
            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Authentication failed");
            }

            localStorage.setItem("user", JSON.stringify(data));
            onLoginSuccess(data);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-wrapper" style={{ position: "relative", minHeight: "100vh" }}>
            <div style={{ position: "absolute", top: "20px", right: "20px", zIndex: 10 }}>
                <ThemeToggle />
            </div>

            <form className="auth-container" onSubmit={handleSubmit}>
                <h2>{isRegister ? "Create Account" : "Welcome Back"}</h2>
                {error && <div className="auth-error">{error}</div>}

                <div className="auth-group">
                    <label>Email</label>
                    <input
                        type="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>

                <div className="auth-group">
                    <label>Password</label>
                    <input
                        type="password"
                        required
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>

                <button type="submit" className="auth-btn">
                    {isRegister ? "Register" : "Login"}
                </button>

                <p className="auth-switch">
                    {isRegister ? "Already have an account? " : "New to the platform? "}
                    <span onClick={() => { setIsRegister(!isRegister); setError(""); }}>
                        {isRegister ? "Log In" : "Sign Up"}
                    </span>
                </p>
            </form>
        </div>
    );
}

export default Auth;