import "./CreateFood.css";
import { useState } from "react";

function CreateFood({ onCreateFood }) {
    const [name, setName] = useState("");
    const [calories, setCalories] = useState("");
    const [carbs, setCarbs] = useState("");
    const [protein, setProtein] = useState("");
    const [fat, setFat] = useState("");

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!name || !calories || !carbs || !protein || !fat) {
            alert("Please fill out all fields!");
            return;
        }

        onCreateFood({
            name,
            calories: Number(calories),
            carbs: Number(carbs),
            protein: Number(protein),
            fat: Number(fat)
        });

        setName("");
        setCalories("");
        setCarbs("");
        setProtein("");
        setFat("");
    };

    return (
        <form className="create-food-container" onSubmit={handleSubmit}>
            <h3 className="create-food-title">Create Custom Food (per 100g)</h3>

            <div className="input-group">
                <label>Food Name:</label>
                <input
                    type="text"
                    required
                    placeholder="e.g., Avocado"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
            </div>

            <div className="input-group">
                <label>Calories (kcal):</label>
                <input
                    type="number"
                    required
                    placeholder="0"
                    value={calories}
                    onChange={(e) => setCalories(e.target.value)}
                />
            </div>

            <div className="macros-input-row" style={{ display: "flex", gap: "10px" }}>
                <div className="input-group" style={{ flex: 1 }}>
                    <label>Carbs (g):</label>
                    <input
                        type="number"
                        required
                        placeholder="0"
                        value={carbs}
                        onChange={(e) => setCarbs(e.target.value)}
                    />
                </div>

                <div className="input-group" style={{ flex: 1 }}>
                    <label>Protein (g):</label>
                    <input
                        type="number"
                        required
                        placeholder="0"
                        value={protein}
                        onChange={(e) => setProtein(e.target.value)}
                    />
                </div>

                <div className="input-group" style={{ flex: 1 }}>
                    <label>Fat (g):</label>
                    <input
                        type="number"
                        required
                        placeholder="0"
                        value={fat}
                        onChange={(e) => setFat(e.target.value)}
                    />
                </div>
            </div>

            <button type="submit" className="create-food-btn">Create Food</button>
        </form>
    );
}

export default CreateFood;