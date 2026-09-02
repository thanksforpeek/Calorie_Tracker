import WeekCalendar from "../../components/calendar/WeekCalendar.jsx";
import NutritionCard from "../../components/log/jsx/NutritionCard.jsx";
import FoodLog from "../../components/log/jsx/FoodLog.jsx";
import FoodDiary from "../../components/diary/FoodDiary.jsx";
import Auth from "../../components/auth/Auth.jsx";
import Targets from "../../components/auth/Targets.jsx";
import CalorieChart from "../../components/log/jsx/CalorieChart.jsx";
import ThemeToggle from "../../components/ui/ThemeToggle.jsx";
import "./index.css";
import { useState, useEffect } from "react";
import { API_BASE_URL } from '../../utils/config';

const getTodayString = () => {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
};

function HomePage() {
    const [user, setUser] = useState(null);
    const [selectedDate, setSelectedDate] = useState(getTodayString());
    const [diaryItems, setDiaryItems] = useState([]);
    const [loggedMeals, setLoggedMeals] = useState([]);

    useEffect(() => {
        const cachedUser = localStorage.getItem("user");
        if (cachedUser) {
            setUser(JSON.parse(cachedUser));
        }
    }, []);

    useEffect(() => {
        if (!user || !user.target_calories) return;

        fetch(`${API_BASE_URL}/api/foods/search`)
            .then(res => res.json())
            .then(data => {
                const formatted = data.map(f => ({
                    id: f.id,
                    name: f.name,
                    calories_per_100g: f.calories_per_100g,
                    carbs_per_100g: f.carbs_per_100g,
                    protein_per_100g: f.protein_per_100g,
                    fat_per_100g: f.fat_per_100g
                }));
                setLoggedMeals(formatted);
            })
            .catch(err => console.error("Error fetching foods:", err));
    }, [user]);

    useEffect(() => {
        if (!user || !user.target_calories) return;

        fetch(`${API_BASE_URL}/api/food-logs?date=${selectedDate}&user_id=${user.id}`)
            .then(res => res.json())
            .then(data => {
                const formattedLogs = data.map(log => {
                    const scale = log.serving_size_g / 100;
                    return {
                        id: log.id,
                        name: log.food_name,
                        category: log.meal_type,
                        gram: log.serving_size_g,
                        calories: Math.round(log.calories_per_100g * scale),
                        carbs: Math.round((log.carbs_per_100g || 0) * scale),
                        protein: Math.round((log.protein_per_100g || 0) * scale),
                        fats: Math.round((log.fat_per_100g || 0) * scale)
                    };
                });
                setDiaryItems(formattedLogs);
            })
            .catch(err => console.error("Error fetching logs:", err));
        }, [user, selectedDate]);

    const handleLogout = () => {
        localStorage.removeItem("user");
        setUser(null);
        setDiaryItems([]);
    };

    const handleCreateCustomFood = async (newFoodData) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/foods`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: newFoodData.name,
                    calories_per_100g: newFoodData.calories,
                    carbs_per_100g: newFoodData.carbs,
                    protein_per_100g: newFoodData.protein,
                    fat_per_100g: newFoodData.fat,
                    is_custom: true,
                    created_by_user_id: user.id
                })
            });

            const savedFood = await response.json();
            if (response.ok) {
                setLoggedMeals([...loggedMeals, {
                    id: savedFood.id,
                    name: savedFood.name,
                    calories_per_100g: savedFood.calories_per_100g,
                    carbs_per_100g: savedFood.carbs_per_100g || 0,
                    protein_per_100g: savedFood.protein_per_100g || 0,
                    fat_per_100g: savedFood.fat_per_100g || 0
                }]);
            }
        } catch (err) {
            console.error("Error creating custom food entry:", err);
        }
    };

    const handleAddFoodToDiary = async (scaledMeal, targetCategory) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/food-logs`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_id: user.id,
                    food_id: scaledMeal.id,
                    meal_type: targetCategory,
                    serving_size_g: scaledMeal.gram,
                    log_date: selectedDate
                })
            });

            const savedLog = await response.json();

            if (response.ok) {
                setDiaryItems([...diaryItems, {
                    id: savedLog.id,
                    name: scaledMeal.name,
                    category: targetCategory,
                    gram: scaledMeal.gram,
                    calories: scaledMeal.calories,
                    carbs: scaledMeal.carbs,
                    protein: scaledMeal.protein,
                    fats: scaledMeal.fats
                }]);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpdateFood = async (id, newGram) => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/food-logs/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ serving_size_g: newGram })
        });

        if (response.ok) {
            const updatedLogsRes = await fetch(
                `${API_BASE_URL}/api/food-logs?date=${selectedDate}&user_id=${user.id}`
            );
            const data = await updatedLogsRes.json();

            const formattedLogs = data.map((log) => {
                const scale = log.serving_size_g / 100;
                return {
                    id: log.id,
                    name: log.food_name,
                    category: log.meal_type,
                    gram: log.serving_size_g,
                    calories: Math.round(log.calories_per_100g * scale),
                    carbs: Math.round((log.carbs_per_100g || 0) * scale),
                    protein: Math.round((log.protein_per_100g || 0) * scale),
                    fats: Math.round((log.fat_per_100g || 0) * scale)
                };
            });

            setDiaryItems(formattedLogs);
        }
    } catch (err) {
        console.error("Error updating log item:", err);
    }
};

    const handleRemoveFood = async (id) => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/food-logs/${id}`, {
                method: "DELETE"
            });
            if (response.ok) {
                setDiaryItems(diaryItems.filter(item => item.id !== id));
            }
        } catch (err) {
            console.error(err);
        }
    };

    const [weeklySummary, setWeeklySummary] = useState([]);

    useEffect(() => {
        if (!user) return;

        fetch(`${API_BASE_URL}/api/food-logs/weekly-summary?user_id=${user.id}&start_date=2026-08-31`)
            .then((res) => res.json())
            .then((data) => setWeeklySummary(data))
            .catch((err) => console.error(err));
    }, [user, diaryItems]);

    if (!user) {
        return <Auth onLoginSuccess={(loggedInUser) => setUser(loggedInUser)} />;
    }

    if (!user.target_calories) {
        return <Targets userId={user.id} onTargetsSaved={(updatedUser) => setUser(updatedUser)} />;
    }

    return (
        <div className="home">
            <div style={{ position: "absolute", top: "20px", right: "20px", display: "flex", gap: "10px" }}>
                <ThemeToggle />
                <button onClick={handleLogout} className="logout-btn">
                    Log Out
                </button>
            </div>

            <WeekCalendar selectedDate={selectedDate} onSelectDate={setSelectedDate} />

            <div className="main-content">
                <div className="left-side">
                    <FoodDiary items={diaryItems} onRemoveFood={handleRemoveFood} onUpdateFood={handleUpdateFood}/>
                </div>

                <div className="right-side">
                    <NutritionCard userTargets={user} diaryItems={diaryItems} />
                    <CalorieChart weekLogs={weeklySummary} targetCalories={user.target_calories}/>
                    <FoodLog loggedMeals={loggedMeals} onAddFood={handleAddFoodToDiary} onCreateFood={handleCreateCustomFood}/>
                </div>
            </div>
        </div>
    );
}

export default HomePage;