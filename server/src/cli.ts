import readline from 'readline';
import { processCommand } from './langchain';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function prompt() {
  rl.question('> ', async (command) => {
    if (command.toLowerCase() === 'exit') {
      rl.close();
      return;
    }
    const response = await processCommand(command);
    console.log(response);
    prompt();
  });
}

console.log('CLI started. Type your commands:');
prompt();
