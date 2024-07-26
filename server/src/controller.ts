import robot from 'robotjs';
import { Server } from 'socket.io';

export function setupController(io: Server) {
  io.on('connection', (socket) => {
    socket.on('action', (action) => {
      // Handle actions here
    });
  });
}
