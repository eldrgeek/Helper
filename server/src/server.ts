import express from 'express';
import http from 'http';
import { Server, Socket } from 'socket.io';
import path from 'path';
import dotenv from 'dotenv';
import { v4 as uuidv4 } from 'uuid';
import { handleCommand } from './commandHandler';
import webpack from 'webpack';
import webpackDevMiddleware from 'webpack-dev-middleware';
import webpackHotMiddleware from 'webpack-hot-middleware';
const config = require('../../webpack.config.ts.js');

import { createProxyMiddleware } from 'http-proxy-middleware';

dotenv.config()

const app = express();
const server = http.createServer(app);
const io = new Server(server);
io.setMaxListeners(20); // Increase the max listeners limit

const PORT = process.env.PORT || 3001;

// Define types for our state and sessions
interface TabInfo {
  id: string;
  url: string;
  title: string;
}

interface StateStructure {
  server: {
    version: string;
    start: string;
    time: number;
  };
  monitor: {
    socket: Socket | null;
  };
  controller: {
    socket: Socket | null;
  };
  extension: {
    socket: Socket | null;
    tabs: TabInfo[];
    llmTabs: TabInfo[];
  };
  logger: {
    socket: Socket | null;
  };
}

interface SessionInfo {
  componentType: string;
  socket: Socket;
}

// Initialize sessions Map
const sessions = new Map<string, SessionInfo>();

// State structure
const state: StateStructure = {
  server: {
    version: '1.0.0',
    start: new Date().toISOString(),
    time: 0,
  },
  monitor: { socket: null },
  controller: { socket: null },
  extension: {
    socket: null,
    tabs: [],
    llmTabs: [],
  },
  logger: { socket: null },
};

const isDevelopment = process.env.NODE_ENV !== 'production';

if (isDevelopment) {
  const compiler = webpack(config);

  app.use(webpackDevMiddleware(compiler, {
    publicPath: config.output.publicPath,
  }));
  app.use(webpackHotMiddleware(compiler));

  app.use(express.static(path.join(__dirname, '../client/public')));

  app.use('*', (req, res, next) => {
    if (compiler.outputFileSystem) {
      const filename = path.join(compiler.outputPath, 'index.html');
      compiler.outputFileSystem.readFile(filename, (err: NodeJS.ErrnoException | null, result: Buffer | undefined) => {
        if (err) {
          return next(err);
        }
        if (result) { // Check if result is defined
          res.set('content-type', 'text/html');
          res.send(result);
          res.end();
        } else {
          next(new Error('File not found'));
        }
      });
    } else {
      next(new Error('Output file system is not available'));
    }
  });

  // Add API proxy
  const apiProxy = createProxyMiddleware({ target: 'http://localhost:9000', changeOrigin: true });
  app.use((req, res, next) => {
    if (req.url.startsWith('/api')) {
      apiProxy(req, res, next);
    } else {
      next();
    }
  });

} else {
  // Serve static files from the build directory in production
  app.use(express.static(path.join(__dirname, '../../client/build')));
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {

    app.get('*', (req, res) => {
      res.sendFile(path.join(__dirname, '../../client/build', 'index.html'));
    });
  });

  // Serve ui.tsx at the root
  app.get('/', (_, res) => {
    res.sendFile(path.join(__dirname, '../../client/build', 'index.html'));
  });
}

io.on('connection', (socket: Socket) => {
    console.log('A user connected');


    // Check if the connected socket is the logger
    socket.on('requestLogger', () => {
      state.logger.socket = socket;
      console.log('Logger connected');
    });

    // Handle session requests
    socket.on('requestSession', (componentType: string) => {
      const sessionId = uuidv4();
      sessions.set(sessionId, { componentType, socket });
      socket.emit('sessionAssigned', sessionId);

      // Update state based on component type
      switch (componentType) {
        case 'monitor':
          state.monitor.socket = socket;
          break;
        case 'controller':
          state.controller.socket = socket;
          break;
        case 'extension':
          state.extension.socket = socket;
          break;
      }
    });

    // Handle disconnections
    socket.on('disconnect', () => {
      console.log('A user disconnected');
      // Remove the session and update state
      for (const [sessionId, session] of sessions.entries()) {
        if (session.socket === socket) {
          sessions.delete(sessionId);
          switch (session.componentType) {
            case 'monitor':
              state.monitor.socket = null;
              break;
            case 'controller':
              state.controller.socket = null;
              break;
            case 'extension':
              state.extension.socket = null;
              break;
          }
          break;
        }
      }
    });

    // Handle tab updates from extension
    socket.on('updateTab', (tabInfo: any) => {
      const existingTabIndex = state.extension.tabs.findIndex(tab => tab.id === tabInfo.id);
      if (existingTabIndex !== -1) {
        state.extension.tabs[existingTabIndex] = tabInfo;
      } else {
        state.extension.tabs.push(tabInfo);
      }
    });


    // Handle LLM tab updates
    socket.on('updateLLMTab', (tabInfo: any) => {
      const existingTabIndex = state.extension.llmTabs.findIndex(tab => tab.id === tabInfo.id);
      if (existingTabIndex !== -1) {
        state.extension.llmTabs[existingTabIndex] = tabInfo;
      } else {
        state.extension.llmTabs.push(tabInfo);
      }
    });

    // Handle command messages
    socket.on('command', async (message) => {
      try {
        const response = await handleCommand(message);
        socket.emit('commandResponse', response);
      } catch (error) {
        console.error('Error handling command:', error);
        socket.emit('commandResponse', { error: 'An error occurred while processing the command' });
      }
    });


    // Handle event messages
    socket.on('event', (data) => {
      // console.log('SERVER RECEIVED event',data)
      if (state.logger.socket) {
        state.logger.socket.emit('message', data);
      }
    });
  });

  // Update server running time every second
  setInterval(() => {
    const currentTime = new Date();
    const startTime = new Date(state.server.start);
    state.server.time = Math.floor((currentTime.getTime() - startTime.getTime()) / 1000);
  }, 1000);

  server.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });

  // Error handling middleware
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {

    console.error(err.stack);
    res.status(500).send('Something broke!');
  });

  export { io, state };