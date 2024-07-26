import React, { useState, useEffect, useCallback } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import { io, Socket } from 'socket.io-client';
import { FaCircle } from 'react-icons/fa';
import styled from 'styled-components';

const Container = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Arial', sans-serif;
`;

const StatusBar = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  gap: 0.5rem;
`;

const Dashboard = styled.div`
  background-color: #f0f0f0;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
`;

const EditorContainer = styled.div`
  margin-bottom: 1rem;
`;

const SubmitButton = styled.button`
  background-color: #0070f3;
  color: white;
  font-size: 1rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #0051bb;
  }
`;

const OutputContainer = styled.div`
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 1rem;
  min-height: 200px;
`;

const UI: React.FC = () => {
  const [output, setOutput] = useState('');
  const [serverStatus, setServerStatus] = useState(false);
  const [componentStatus, setComponentStatus] = useState({
    monitor: false,
    controller: false,
    extension: false,
  });
  const [dashboardData, setDashboardData] = useState({
    tabCount: 0,
    llmTabCount: 0,
  });
  const [socket, setSocket] = useState<Socket | null>(null);

  const inputEditor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: 'Type your command here...' }),
    ],
    content: '',
  });

  const outputEditor = useEditor({
    extensions: [StarterKit],
    content: '',
    editable: false,
  });

  useEffect(() => {
    const newSocket = io('http://localhost:3001');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      setServerStatus(true);
      newSocket.emit('requestSession', 'ui');
    });

    newSocket.on('disconnect', () => setServerStatus(false));

    newSocket.on('componentStatus', (status) => setComponentStatus(status));
    newSocket.on('dashboardUpdate', (data) => setDashboardData(data));
    newSocket.on('serverMessage', (message) => {
      if (outputEditor) {
        outputEditor.commands.setContent(outputEditor.getHTML() + '<p>' + message + '</p>');
      }
    });

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const handleSubmit = useCallback(() => {
    if (inputEditor && socket) {
      const command = inputEditor.getText();
      socket.emit('command', command);
      inputEditor.commands.setContent('');
    }
  }, [inputEditor, socket]);

  const handleKeyDown = useCallback((event: React.KeyboardEvent) => {
    if (event.ctrlKey && event.key === 'Enter') {
      handleSubmit();
    }
  }, [handleSubmit]);

  return (
    <Container>
      <StatusBar>
        <StatusItem>
          Server: <FaCircle color={serverStatus ? 'green' : 'red'} />
        </StatusItem>
        <StatusItem>
          Monitor: <FaCircle color={componentStatus.monitor ? 'green' : 'red'} />
        </StatusItem>
        <StatusItem>
          Controller: <FaCircle color={componentStatus.controller ? 'green' : 'red'} />
        </StatusItem>
        <StatusItem>
          Extension: <FaCircle color={componentStatus.extension ? 'green' : 'red'} />
        </StatusItem>
      </StatusBar>
      <Dashboard>
        <h3>Dashboard (Low-res)</h3>
        <p>Total Tabs: {dashboardData.tabCount}</p>
        <p>LLM Tabs: {dashboardData.llmTabCount}</p>
      </Dashboard>
      <EditorContainer>
        <EditorContent editor={inputEditor} onKeyDown={handleKeyDown} />
        <SubmitButton onClick={handleSubmit}>Submit</SubmitButton>
      </EditorContainer>
      <OutputContainer>
        <EditorContent editor={outputEditor} />
      </OutputContainer>
    </Container>
  );
};

export default UI;