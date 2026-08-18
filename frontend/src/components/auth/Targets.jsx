import { useState } from "react";
import "./Auth.css";
import ThemeToggle from "../ui/ThemeToggle";
import { API_BASE_URL } from '../../utils/config';

const activityMultipliers = {
    "Sedentary" : 1.2,
    "Lightly active" : 1.375,
    "Moderately active" : 1.55,
    "Very active" : 1.725,
    "Extremely active" : 1.9
}

function Targets({ userId, onTargetsSaved }) {
    const [weight, setWeight] = useState("");
    const [height, setHeight] = useState("");
    const [age, setAge] = useState("");
    const [activityLevel, setActivityLevel] = useState("Moderately active");
    const [calories, setCalories] = useState("");
    const [protein, setProtein] = useState("");
    const [carbs, setCarbs] = useState("");
    const [fats, setFats] = useState("");
    const [error, setError] = useState("");
    const [isManual, setIsManual] = useState(false)

    const baseBmr = (10 * weight) + (6.25 * height) - (5 * age)
    const bmr = baseBmr * activityMultipliers[activityLevel]

    const countProtein = (bmr * 0.3) / 4
    const countCarbs = (bmr * 0.4) / 4
    const countFat = (bmr * 0.3) / 9

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        const payload = {
            weight_kg: parseFloat(weight),
            height_cm: parseInt(height),
            age: parseInt(age),
            activity_level: activityLevel,
            target_calories: isManual ? parseInt(calories) : Math.round(bmr),
            target_protein: isManual ? parseInt(protein) : Math.round(countProtein),
            target_carbs: isManual ? parseInt(carbs) : Math.round(countCarbs),
            target_fats: isManual ? parseInt(fats) : Math.round(countFat)
        };

        try {
            const response = await fetch(`${API_BASE_URL}/api/users/${userId}/targets`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const updatedUser = await response.json();

            if (!response.ok) {
                throw new Error(updatedUser.detail || "Failed to update targets");
            }

            localStorage.setItem("user", JSON.stringify(updatedUser));
            onTargetsSaved(updatedUser);
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="targets-wrapper" style={{ position: "relative", minHeight: "100vh" }}>
            <div style={{ position: "absolute", top: "20px", right: "20px", zIndex: 10 }}>
                <ThemeToggle />
            </div>
            
            <form className="targets-container" onSubmit={handleSubmit}>
                <h2>Set Your Nutritional Targets</h2>
                {error && <div className="auth-error">{error}</div>}

                <div className="targets-grid">
                    <div className="auth-group">
                        <label>Weight (kg)</label>
                        <input type="number" required value={weight} onChange={(e) => setWeight(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Height (cm)</label>
                        <input type="number" required value={height} onChange={(e) => setHeight(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Age</label>
                        <input type="number" required value={age} onChange={(e) => setAge(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Activity Level</label>
                        <select value={activityLevel} onChange={(e) => setActivityLevel(e.target.value)}>
                            <option value="Sedentary">Sedentary</option>
                            <option value="Lightly active">Lightly active</option>
                            <option value="Moderately active">Moderately active</option>
                            <option value="Very active">Very active</option>
                            <option value="Extremely active">Extremely active</option>
                        </select>
                    </div>
                </div>

                {isManual && (
                    <div className="targets-grid macro-grid">
                    <div className="auth-group">
                        <label>Calories Target</label>
                        <input type="number" required value={calories} onChange={(e) => setCalories(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Protein (g)</label>
                        <input type="number" required value={protein} onChange={(e) => setProtein(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Carbs (g)</label>
                        <input type="number" required value={carbs} onChange={(e) => setCarbs(e.target.value)} />
                    </div>
                    <div className="auth-group">
                        <label>Fats (g)</label>
                        <input type="number" required value={fats} onChange={(e) => setFats(e.target.value)} />
                    </div>
                </div>
                )}

                <input type="checkbox" id="targets-option" defaultChecked={isManual} onChange={(e => setIsManual(e.target.checked))} />
                <label htmlFor="targets-option">Do you want to set targets manually?</label>
                <button type="submit" className="targets-btn">Save & Continue</button>
            </form>
        </div>
    );
}

export default Targets;