import "../css/FoodLog.css";
import FoodRow from "./FoodRow.jsx";
import CreateFood from "../../form/CreateFood.jsx";
import { useState } from "react";

function FoodLog({ loggedMeals = [], onAddFood, onCreateFood }) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");

    const handleCreateAndClose = (newFoodData) => {
        onCreateFood(newFoodData);
        setIsModalOpen(false);
    };

    const filteredMeals = loggedMeals.filter((meal) =>
        meal.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="food-log-container">
            <div className="food-log-header">
                <h3>Add Food</h3>
                <button className="add-custom-btn" onClick={() => setIsModalOpen(true)}>
                    + Custom Food
                </button>
            </div>

            <div className="search-bar-container">
                <input
                    type="text"
                    className="food-search-input"
                    placeholder="Search food..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            <div className="food-log-list">
                {filteredMeals.length > 0 ? (
                    filteredMeals.map((meal) => (
                        <FoodRow key={meal.id} meal={meal} onAddFood={onAddFood} />
                    ))
                ) : (
                    <p className="no-foods-found">No food found...</p>
                )}
            </div>

            {isModalOpen && (
                <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close-btn" onClick={() => setIsModalOpen(false)}>
                            ✕
                        </button>
                        <CreateFood onCreateFood={handleCreateAndClose} />
                    </div>
                </div>
            )}
        </div>
    );
}

export default FoodLog;