import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";
import "../css/CalorieChart.css";

function CalorieChart({ weekLogs = [], targetCalories = 2000 }) {

    return (
        <div className="calorie-chart-card">
            <div className="chart-header">
                <h3>Weekly Calorie Trend</h3>
                <span className="target-badge">Target: {targetCalories} kcal</span>
            </div>

            <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={220}>
                    <AreaChart data={weekLogs} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorCal" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                            </linearGradient>
                        </defs>

                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />
                        <YAxis axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} />

                        <Tooltip content={<CustomTooltip />} />

                        <ReferenceLine y={targetCalories} stroke="#ef4444" strokeDasharray="4 4" />

                        <Area
                            type="monotone"
                            dataKey="calories"
                            stroke="#3b82f6"
                            strokeWidth={3}
                            fillOpacity={1}
                            fill="url(#colorCal)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

function CustomTooltip({ active, payload, label }) {
    if (active && payload && payload.length) {
        return (
            <div className="custom-tooltip">
                <p className="tooltip-day">{label}</p>
                <p className="tooltip-calories">{payload[0].value} kcal</p>
            </div>
        );
    }
    return null;
}

export default CalorieChart;