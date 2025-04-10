import { GasFee } from "../types/gas";

let socket: WebSocket | null = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 5000; // 5 seconds

export const connectToGasWebSocket = (
  onData: (data: GasFee[]) => void,
  onError?: (error: string) => void
) => {
  if (socket) {
    socket.close();
  }

  socket = new WebSocket('ws://localhost:8000/ws/gas');

  socket.onopen = () => {
    console.log('WebSocket connection established');
    reconnectAttempts = 0;
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onData(data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
      onError?.('Error parsing gas data');
    }
  };

  socket.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError?.('WebSocket connection error');
  };

  socket.onclose = () => {
    console.log('WebSocket connection closed');
    if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      reconnectAttempts++;
      setTimeout(() => {
        connectToGasWebSocket(onData, onError);
      }, RECONNECT_DELAY);
    } else {
      onError?.('Failed to establish WebSocket connection after multiple attempts');
    }
  };
};

export const disconnectFromGasWebSocket = () => {
  if (socket) {
    socket.close();
    socket = null;
  }
};
