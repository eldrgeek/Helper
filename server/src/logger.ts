import { io } from 'socket.io-client';
import winston from 'winston';

const { format } = require('logform');

const alignedWithColorsAndTime = format.combine(
  format.colorize(),
  format.timestamp(),
  format.align(),
  format.printf((info: winston.LogEntry) => `event: ${info.timestamp} ${info.level}: ${info.message}`)
);
const socket = io('http://localhost:3001');
let lastErrorTime: number | null = null;
const errorInterval = 5000; // 5 seconds

socket.on('connect', () => {
  console.log('Logger connected');
  socket.emit('requestLogger'); // Send requestLogger message upon connection
});

socket.on('connect_error', (error) => {
  handleConnectionError(error);
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});

socket.on('message', (data) => {
  console.log("DATA TO LOGGER IS", typeof data, data);
  try {
    if (data.type == 'keyboard' || data.type == 'mouse') {
     switch(data.op){
      case "press":
        monitorlogger.info(`press ${data.key}`);
        break;
      case "click":
        monitorlogger.info(`click ${data.x} ${data.y}`);
        break;
     }

    }
  } catch (error) {
    if (error instanceof Error) {
      logger.error(`Invalid JSON received: ${error.message}`);
    } else {
      logger.error('Invalid JSON received: Unknown error');
    }
    process.exit(1); // Exit with an error code
  }
});

// Handle connection errors
function handleConnectionError(error: Error) {
  const currentTime = Date.now();
  if (lastErrorTime === null || currentTime - (lastErrorTime ?? currentTime) >= errorInterval) {
    logger.error(`Failed to connect: ${error.message}`);
    lastErrorTime = currentTime;
  }
}
const monitorlogger = winston.createLogger({
  level: 'info',
  format: alignedWithColorsAndTime,

  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'kbd.log' }),
    // {{ edit_1 }}: Add console transport for error logging
    new winston.transports.Console({
      format: winston.format.cli(),
    }),
  ],
});
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'user-service' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
    // {{ edit_1 }}: Add console transport for error logging
    new winston.transports.Console({
      level: 'error', // Log errors to console
      // format: winston.format.simple(),
      format: winston.format.cli(),
    }),
  ],
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple(),
  }));
  // Retry connecting every second if disconnected
  setInterval(() => {
    if (!socket.connected) {
      socket.connect();
    }
  }, 1000);
}