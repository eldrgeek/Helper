import { ChatOpenAI } from 'langchain/chat_models/openai';
import { HumanMessage } from 'langchain/schema';

const chat = new ChatOpenAI({ temperature: 0 });

export async function processCommand(command: string) {
  const response = await chat.call([
    new HumanMessage(command),
  ]);
  return response.content;
}
