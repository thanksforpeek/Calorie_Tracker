import "./WeekCalendar.css";

function WeekCalendar({ selectedDate, onSelectDate }) {
    const daysOfWeek = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
    };

    const today = new Date();
    const jsDay = today.getDay();
    const currentDayIndex = jsDay === 0 ? 6 : jsDay - 1;

    const calendarDays = daysOfWeek.map((name, index) => {
        const dayDate = new Date(today);
        const offset = index - currentDayIndex;
        dayDate.setDate(today.getDate() + offset);

        const dateString = formatDate(dayDate);

        return {
            name: name,
            dateNumber: dayDate.getDate(),
            fullDate: dateString,
            index: index
        };
    });

    return (
        <div className="calendar-card">
            <ul className="calendar-row">
                {calendarDays.map((day) => {
                    const isSelected = day.fullDate === selectedDate;

                    return (
                        <li
                            key={day.fullDate}
                            className={`calendar-cell ${isSelected ? "active" : ""}`}
                            onClick={() => onSelectDate(day.fullDate)}
                        >
                            <span className="day-label">{day.name}</span>
                            <span className="day-digit">{day.dateNumber}</span>
                        </li>
                    );
                })}
            </ul>
        </div>
    );
}

export default WeekCalendar;