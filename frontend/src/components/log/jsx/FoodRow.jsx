import { useState } from "react";

function FoodRow({ meal, onAddFood }) {
    const [category, setCategory] = useState("Breakfast");
    const [gramsInput, setGramsInput] = useState(100);
    const scaleFactor = gramsInput / 100;
    const previewCalories = Math.round(meal.calories_per_100g * scaleFactor);
    const previewCarbs = Math.round(meal.carbs_per_100g * scaleFactor);
    const previewProtein = Math.round(meal.protein_per_100g * scaleFactor);
    const previewFat = Math.round(meal.fat_per_100g * scaleFactor);

    const handleAddClick = () => {
        if (!gramsInput || gramsInput <= 0) return;

        onAddFood({
            id: meal.id,
            name: meal.name,
            gram: Number(gramsInput),
            calories: previewCalories,
            carbs: previewCarbs,
            protein: previewProtein,
            fats: previewFat
        }, category);
    };

    return (
        <div className="food-row">
            <div className="food-info-block">
                <span className="food-name">{meal.name}</span>
                <span className="food-stats">
                    {previewCalories} cal | C: {previewCarbs}g · P: {previewProtein}g · F: {previewFat}g
                </span>
            </div>

            <div className="action-group">
                <input
                    type="number"
                    className="grams-input"
                    value={gramsInput}
                    onChange={(e) => setGramsInput(e.target.value)}
                    style={{ width: "60px", padding: "6px", borderRadius: "6px", border: "1px solid #e2e8f0" }}
                />
                <span style={{ fontSize: "13px", color: "#64748b" }}>g</span>

                <select className="category-dropdown" value={category} onChange={(e) => setCategory(e.target.value)}>
                    <option value="Breakfast">Breakfast</option>
                    <option value="Lunch">Lunch</option>
                    <option value="Dinner">Dinner</option>
                </select>

                <button className="row-action-btn" onClick={handleAddClick}>+</button>
            </div>
        </div>
    );
}

export default FoodRow;