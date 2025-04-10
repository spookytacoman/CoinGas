
import { HistoricalGasData } from '@/types/gas';

// Mock historical gas data
export const fetchHistoricalGasData = async (network: string): Promise<HistoricalGasData[]> => {
  // In a real application, this would fetch data from an API
  return new Promise((resolve) => {
    setTimeout(() => {
      // Generate random historical data for the past 30 days
      const data: HistoricalGasData[] = [];
      const now = new Date();
      
      for (let i = 30; i >= 0; i--) {
        const date = new Date();
        date.setDate(now.getDate() - i);
        
        data.push({
          date: date.toISOString(),
          low: Math.round(Math.random() * 50 + 10),
          medium: Math.round(Math.random() * 80 + 30),
          high: Math.round(Math.random() * 120 + 60),
        });
      }
      
      resolve(data);
    }, 800);
  });
};
