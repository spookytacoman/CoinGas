import { GasFee } from "../types/gas";

let socket: WebSocket | null = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 5000; // 5 seconds
let isIntentionalClose = false;
let heartbeatInterval: NodeJS.Timeout | null = null;
let isConnecting = false;

// Get the WebSocket URL from environment or use default
const getWebSocketUrl = () => {
  // Check if we're in development or production
  const isDev = import.meta.env.DEV;
  const port = isDev ? '8000' : window.location.port;
  const host = isDev ? 'localhost' : window.location.hostname;
  
  return `ws://${host}:${port}/ws/gas`;
};

const startHeartbeat = (ws: WebSocket) => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
  }
  
  heartbeatInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send('ping');
    }
  }, 30000); // Send heartbeat every 30 seconds
};

const stopHeartbeat = () => {
  if (heartbeatInterval) {
    clearInterval(heartbeatInterval);
    heartbeatInterval = null;
  }
};

const cleanupExistingConnection = async () => {
  if (socket) {
    isIntentionalClose = true;
    stopHeartbeat();
    
    if (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING) {
      socket.close();
    }
    
    socket = null;
    isConnecting = false;
  }
};

export const connectToGasWebSocket = async (
  onData: (data: GasFee[]) => void,
  onError?: (error: string) => void
) => {
  // Prevent multiple simultaneous connection attempts
  if (isConnecting) {
    console.log('Connection attempt already in progress');
    return;
  }

  if (socket?.readyState === WebSocket.OPEN) {
    console.log('WebSocket already connected');
    return;
  }

  try {
    isConnecting = true;
    await cleanupExistingConnection();
    
    const wsUrl = getWebSocketUrl();
    console.log(`Connecting to WebSocket at: ${wsUrl}`);
    
    socket = new WebSocket(wsUrl);
    isIntentionalClose = false;

    socket.onopen = () => {
      console.log('WebSocket connection established');
      reconnectAttempts = 0;
      isConnecting = false;
      startHeartbeat(socket!);
    };

    socket.onmessage = (event) => {
      try {
        if (event.data === 'pong') {
          console.debug('Received heartbeat response');
          return;
        }
        
        const data = JSON.parse(event.data);
        console.log('Received WebSocket data:', data);
        onData(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
        onError?.('Error parsing gas data');
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      isConnecting = false;
      onError?.('WebSocket connection error');
    };

    socket.onclose = (event) => {
      console.log(`WebSocket connection closed with code: ${event.code}, reason: ${event.reason}`);
      stopHeartbeat();
      isConnecting = false;
      
      // Only attempt to reconnect if the close wasn't intentional
      if (!isIntentionalClose && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
        setTimeout(() => {
          connectToGasWebSocket(onData, onError);
        }, RECONNECT_DELAY);
      } else if (!isIntentionalClose) {
        onError?.('Failed to establish WebSocket connection after multiple attempts');
      }
    };
  } catch (error) {
    console.error('Error creating WebSocket:', error);
    isConnecting = false;
    onError?.('Failed to create WebSocket connection');
  }
};

export const disconnectFromGasWebSocket = async () => {
  await cleanupExistingConnection();
  reconnectAttempts = 0;
};
