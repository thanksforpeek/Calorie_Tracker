import "../css/NutritionCard.css";

function NutritionCard({ userTargets, diaryItems = [] }) {
    const maxCalories = userTargets?.target_calories || 2000;
    const maxCarbs = userTargets?.target_carbs || 250;
    const maxProtein = userTargets?.target_protein || 120;
    const maxFat = userTargets?.target_fats || 60;

    const caloriesEaten = diaryItems.reduce((sum, item) => sum + (Number(item.calories) || 0), 0);
    const carbs = diaryItems.reduce((sum, item) => sum + (Number(item.carbs) || 0), 0);
    const protein = diaryItems.reduce((sum, item) => sum + (Number(item.protein) || 0), 0);
    const fat = diaryItems.reduce((sum, item) => sum + (Number(item.fats) || 0), 0);

    const caloriesLeft = maxCalories - caloriesEaten;

    return (
        <>
            <div className="calories-card">
                <p>Calories</p>
                <div className="calories-row">
                    <h3>{caloriesEaten} cal / {maxCalories}</h3>
                    <p>{caloriesLeft < 0 ? 0 : caloriesLeft} left</p>
                </div>
                <progress value={caloriesEaten} max={maxCalories}/>
            </div>

            <div className="macros-card">
                <div className="macros-row">
                    <div className="macro-column">
                        <p>Carbs</p>
                        <h3>{carbs}g / {maxCarbs}g</h3>
                        <progress className="progress-carbs" value={carbs} max={maxCarbs}/>
                    </div>

                    <div className="macro-column">
                        <p>Protein</p>
                        <h3>{protein}g / {maxProtein}g</h3>
                        <progress className="progress-protein" value={protein} max={maxProtein}/>
                    </div>

                    <div className="macro-column">
                        <p>Fat</p>
                        <h3>{fat}g / {maxFat}g</h3>
                        <progress className="progress-fat" value={fat} max={maxFat}/>
                    </div>
                </div>
            </div>
        </>
    );
}

export default NutritionCard;