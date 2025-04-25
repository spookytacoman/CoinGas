import { HistoricalGasData } from '@/types/gas';

const API_BASE_URL = 'http://localhost:8000';

export const fetchHistoricalGasData = async (network: string): Promise<HistoricalGasData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/history/${network}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log("historical Data:")
    console.log(data)
    return data;
  } catch (error) {
    console.error('Error fetching historical gas data:', error);
    throw error;
  }
};
