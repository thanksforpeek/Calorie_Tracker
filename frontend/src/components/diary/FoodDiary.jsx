import { useState } from "react";
import "./FoodDiary.css";

function FoodDiary({ items = [], onRemoveFood, onUpdateFood }) {
    const categories = ["Breakfast", "Lunch", "Dinner"];

    return (
        <div className="food-diary-container">
            <h2 className="diary-title">Today's Log</h2>

            {categories.map((category) => {
                const categoryItems = items.filter((item) => item.category === category);

                return (
                    <div key={category} className="diary-category-section">
                        <h4 className="category-title">{category}</h4>

                        {categoryItems.length > 0 ? (
                            <div className="category-items-list">
                                {categoryItems.map((item) => (
                                    <DiaryRow
                                        key={item.id}
                                        item={item}
                                        onRemoveFood={onRemoveFood}
                                        onUpdateFood={onUpdateFood}
                                    />
                                ))}
                            </div>
                        ) : (
                            <p className="empty-category-text">No food logged yet...</p>
                        )}
                    </div>
                );
            })}
        </div>
    );
}

function DiaryRow({ item, onRemoveFood, onUpdateFood }) {
    const [isEditing, setIsEditing] = useState(false);
    const [gram, setGram] = useState(item.gram);

    const handleSave = () => {
        if (!gram || Number(gram) <= 0) return;
        onUpdateFood(item.id, Number(gram));
        setIsEditing(false);
    };

    return (
        <div className="diary-item-row">
            <span className="diary-item-name">{item.name}</span>

            <div className="diary-item-right">
                {isEditing ? (
                    <div className="edit-mode-container">
                        <input
                            type="number"
                            className="edit-gram-input"
                            value={gram}
                            onChange={(e) => setGram(e.target.value)}
                        />
                        <span className="unit-label">g</span>
                        <button className="save-btn" onClick={handleSave}>
                            Save
                        </button>
                        <button className="cancel-btn" onClick={() => setIsEditing(false)}>
                            ✕
                        </button>
                    </div>
                ) : (
                    <>
                        <span className="diary-item-details">
                            {item.calories} cal, {item.gram} g
                        </span>
                        <button className="edit-btn" onClick={() => setIsEditing(true)}>
                            Edit
                        </button>
                        <button className="remove-btn" onClick={() => onRemoveFood(item.id)}>
                            Remove
                        </button>
                    </>
                )}
            </div>
        </div>
    );
}

export default FoodDiary;