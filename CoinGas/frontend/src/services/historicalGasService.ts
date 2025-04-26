import { HistoricalGasData } from '@/types/gas';

const API_BASE_URL = 'http://localhost:8000';

export const fetchHistoricalGasData = async (network: string): Promise<HistoricalGasData[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/history/${network}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching historical gas data:', error);
    throw error;
  }
};

// Function to send a prediction request via WebSocket and return the prediction data
export const predictTomorrowGas = async (network: string): Promise<HistoricalGasData[]> => {
  return new Promise((resolve, reject) => {
    const socket = new WebSocket('ws://localhost:8000/ws/gas');

    socket.onopen = () => {
      socket.send(JSON.stringify({ action: 'predict', network }));
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.action === 'prediction') {
        socket.close();
        resolve(data.data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      reject(error);
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
    };
  });
};
