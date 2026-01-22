import React from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';

interface ChartProps {
    data: any[];
    productName: string;
}

const ForecastChart: React.FC<ChartProps> = ({ data, productName }) => {
    return (
        <div className="w-full h-[400px] bg-card rounded-lg p-4 shadow-lg border border-border">
            <h3 className="text-xl font-bold mb-4 text-foreground">{productName} - Sales Forecast</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart
                    data={data}
                    margin={{
                        top: 5,
                        right: 30,
                        left: 20,
                        bottom: 5,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="date" stroke="#888" />
                    <YAxis stroke="#888" />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px' }}
                        itemStyle={{ color: '#fff' }}
                    />
                    <Legend />
                    <Line
                        type="monotone"
                        dataKey="actual"
                        stroke="#3b82f6"
                        activeDot={{ r: 8 }}
                        name="Actual Sales"
                        strokeWidth={2}
                    />
                    <Line
                        type="monotone"
                        dataKey="forecast"
                        stroke="#10b981"
                        strokeDasharray="5 5"
                        name="Forecast (SES)"
                        strokeWidth={2}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default ForecastChart;
