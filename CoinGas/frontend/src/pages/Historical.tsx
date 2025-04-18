
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchHistoricalGasData } from '@/services/historicalGasService';
import { HistoricalGasData } from '@/types/gas';
import { toast } from 'sonner';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { format } from 'date-fns';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

const Historical: React.FC = () => {
  const { network } = useParams<{ network: string }>();
  const navigate = useNavigate();
  const [historicalData, setHistoricalData] = useState<HistoricalGasData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!network) return;
      
      try {
        setLoading(true);
        const data = await fetchHistoricalGasData(network);
        setHistoricalData(data);
        setError(null);
      } catch (err) {
        console.error(`Failed to fetch historical gas data for ${network}:`, err);
        setError(`Failed to load historical data for ${network}. Please try again later.`);
        toast.error('Could not load historical gas data', {
          description: 'Please try refreshing the page'
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [network]);

  // Format data for the chart
  const chartData = historicalData.map(item => ({
    date: format(new Date(item.date), 'MMM dd'),
    low: item.low,
    medium: item.medium,
    high: item.high,
  }));

  // Get network name with first letter capitalized
  const networkName = network ? network.charAt(0).toUpperCase() + network.slice(1) : '';

  return (
    <div className="container py-12">
      <div className="flex items-center mb-6">
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={() => navigate('/')}
          className="mr-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold">{networkName} Historical Gas Fees</h1>
      </div>

      {loading && (
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="flex flex-col items-center gap-4">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
            <p className="text-sm text-muted-foreground">Loading historical data...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex justify-center items-center min-h-[50vh]">
          <div className="text-center space-y-4">
            <p className="text-destructive">{error}</p>
            <Button 
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-secondary hover:bg-secondary/80 rounded-md text-sm"
            >
              Return to Dashboard
            </Button>
          </div>
        </div>
      )}

      {!loading && !error && historicalData.length > 0 && (
        <div className="mt-6 rounded-lg border border-white/10 p-6 backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-4">30-Day Gas Fee History</h2>
          <div className="h-[400px] w-full">
            <ChartContainer
              config={{
                low: { 
                  label: "Low Priority", 
                  theme: { light: "#10b981", dark: "#10b981" } 
                },
                medium: { 
                  label: "Medium Priority", 
                  theme: { light: "#f59e0b", dark: "#f59e0b" } 
                },
                high: { 
                  label: "High Priority", 
                  theme: { light: "#ef4444", dark: "#ef4444" } 
                }
              }}
            >
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }} 
                />
                <YAxis 
                  tick={{ fontSize: 12 }} 
                  label={{ 
                    value: 'Gas Price (Gwei)', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { textAnchor: 'middle' }
                  }} 
                />
                <ChartTooltip 
                  content={<ChartTooltipContent />} 
                />
                <Line 
                  type="monotone" 
                  dataKey="low" 
                  name="Low"
                  stroke="#10b981" 
                  strokeWidth={2} 
                  dot={{ r: 3 }} 
                  activeDot={{ r: 5 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="medium" 
                  name="Medium"
                  stroke="#f59e0b" 
                  strokeWidth={2} 
                  dot={{ r: 3 }} 
                  activeDot={{ r: 5 }} 
                />
                <Line 
                  type="monotone" 
                  dataKey="high" 
                  name="High"
                  stroke="#ef4444" 
                  strokeWidth={2} 
                  dot={{ r: 3 }} 
                  activeDot={{ r: 5 }} 
                />
                <Legend />
              </LineChart>
            </ChartContainer>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            Note: This chart shows the historical gas fee trends for {networkName} over the past 30 days.
            Lower values indicate cheaper transaction costs.
          </p>
        </div>
      )}
    </div>
  );
};

export default Historical;
