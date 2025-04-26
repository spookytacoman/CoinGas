import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchHistoricalGasData, predictTomorrowGas } from '@/services/historicalGasService';
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
  const [chartData, setChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPredicted, setIsPredicted] = useState(false);

  
  // Helper function to get the unit for the Y-axis label
  const getGasUnit = () => {
    switch (network) {
      case 'ethereum':
        return 'Gwei';
      case 'bitcoin':
        return 'sat/vB';
      case 'solana':
        return 'SOL';
      default:
        return 'Gas Price';
    }
  };

  // Handle prediction request
  const handlePredictTomorrow = async () => {
    if (!network) return;
    try {
      setLoading(true);
      const prediction = await predictTomorrowGas(network);
      console.log("Raw prediction data:", prediction); // Debug log

      if (!prediction || !Array.isArray(prediction)) {
        toast.error("Invalid prediction data received");
        return;
      }

      const mappedData = prediction.map((item) => {
        // Use `timestamp` if `date` is missing
        const dateStr = item.date || item.timestamp;
        const date = dateStr ? new Date(dateStr) : new Date();

        if (isNaN(date.getTime())) {
          console.error("Invalid date:", dateStr);
          return {
            date: "00:00", // Fallback
            low: item.low || 0,
            medium: item.medium || 0,
            high: item.high || 0,
          };
        }

        return {
          date: format(date, "HH:mm"),
          low: item.low || 0,
          medium: item.medium || 0,
          high: item.high || 0,
        };
      });

      console.log("Mapped chart data:", mappedData); // Debug log
      setChartData(mappedData);
      setIsPredicted(true);
      toast.success("Prediction loaded successfully");
    } catch (err) {
      console.error("Prediction failed:", err);
      toast.error("Failed to load prediction");
    } finally {
      setLoading(false);
    }
  };

  // Revert to original data
  const handleRevert = () => {
    setChartData(
      historicalData
        .filter((item) => {
          const itemDate = new Date(item.date);
          const today = new Date();
          return (
            itemDate.getDate() === today.getDate() &&
            itemDate.getMonth() === today.getMonth() &&
            itemDate.getFullYear() === today.getFullYear()
          );
        })
        .map((item) => ({
          date: format(new Date(item.date), 'HH:mm'),
          low: item.low,
          medium: item.medium,
          high: item.high,
        }))
        .reverse()
    );
    setIsPredicted(false);
  };

  // Retrieve Historical data
  useEffect(() => {
    const fetchData = async () => {
      if (!network) return;
      
      try {
        setLoading(true);
        const data = await fetchHistoricalGasData(network);
        setHistoricalData(data);
        setChartData(
          data
            .filter((item) => {
              const itemDate = new Date(item.date);
              const today = new Date();
              return (
                itemDate.getDate() === today.getDate() &&
                itemDate.getMonth() === today.getMonth() &&
                itemDate.getFullYear() === today.getFullYear()
              );
            })
            .map((item) => ({
              date: format(new Date(item.date), 'HH:mm'),
              low: item.low,
              medium: item.medium,
              high: item.high,
            }))
            .reverse()
        );
        setError(null);
      } catch (err) {
        console.error(`Failed to fetch historical gas data for ${network}:`, err);
        setError(`Failed to load historical data for ${network}. Please try again later.`);
        toast.error('Could not load historical gas data', {
          description: 'Please try refreshing the page',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [network]);

  // Get network name with first letter capitalized
  const networkName = network ? network.charAt(0).toUpperCase() + network.slice(1) : '';

  return (
    <div className="container py-12">
      <div className="flex flex-col mb-6">
        <div className="flex items-center">
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
        <div className="mt-4">
          {!isPredicted ? (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handlePredictTomorrow}
              disabled={loading}
            >
              Predict Tomorrow
            </Button>
          ) : (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRevert}
              disabled={loading}
            >
              Revert
            </Button>
          )}
        </div>
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

      {!loading && !error && chartData.length > 0 && (
        <div className="mt-6 rounded-lg border border-white/10 p-6 backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-4">24-Hour Gas Fee History</h2>
          <div className="h-[400px] h-full min-w-0 overflow-hidden">
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
              <ResponsiveContainer width="100%" height="100%" debounce={1}>
                <LineChart
                  data={chartData}
                  margin={{ top: 20, right: 30, left: 40, bottom: 30 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 10 }}
                    interval={Math.ceil(chartData.length / 6)}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis 
                    tick={{ fontSize: 10 }} 
                    tickFormatter={(value) => Math.abs(value) < 0.001 ? value.toExponential(2) : value.toFixed(2) }
                    label={{ 
                      value: `Gas Price (${getGasUnit()})`, 
                      angle: -90, 
                      position: 'insideLeft',
                      style: { textAnchor: 'middle', fontSize: 12 }
                    }} 
                  />
                  <ChartTooltip 
                    content={({ payload, label }) => {
                      if (!payload || payload.length === 0) return null;

                      return (
                        <div className="bg-background/90 backdrop-blur-sm p-3 rounded-lg border border-white/10 shadow-lg">
                          <p className="text-sm font-medium text-muted-foreground mb-1">
                            {label}
                          </p>
                          {payload.map((entry, index) => {
                            const value = entry.value as number;
                            const formattedValue = Math.abs(value) < 0.001 
                              ? value.toExponential(2) 
                              : value.toFixed(2);
                            return (
                              <div key={`tooltip-${index}`} className="flex items-center justify-between gap-4">
                                <div className="flex items-center gap-2">
                                  <div 
                                    className="h-3 w-3 rounded-full" 
                                    style={{ backgroundColor: entry.color }} 
                                  />
                                  <span className="text-sm capitalize">{entry.name}</span>
                                </div>
                                <span className="text-sm font-semibold">
                                  {formattedValue} {getGasUnit()}
                                </span>
                              </div>
                            );
                          })}
                        </div>
                      );
                    }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="low" 
                    name="Low"
                    stroke="#10b981" 
                    strokeWidth={2} 
                    dot={{ r: 2 }} 
                    activeDot={{ r: 4 }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="medium" 
                    name="Medium"
                    stroke="#f59e0b" 
                    strokeWidth={2} 
                    dot={{ r: 2 }} 
                    activeDot={{ r: 4 }} 
                  />
                  <Line 
                    type="monotone" 
                    dataKey="high" 
                    name="High"
                    stroke="#ef4444" 
                    strokeWidth={2} 
                    dot={{ r: 2 }} 
                    activeDot={{ r: 4 }} 
                  />
                  <Legend 
                    wrapperStyle={{ paddingTop: '20px' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            Note: This chart shows the historical gas fee trends for {networkName} over the past 24 hours.
            Lower values indicate cheaper transaction costs.
          </p>
        </div>
      )}
    </div>
  );
};

export default Historical;
