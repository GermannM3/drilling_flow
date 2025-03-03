// Скрипт для быстрой установки и запуска проекта
const { spawn, exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Цвета для консоли
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  underscore: '\x1b[4m',
  blink: '\x1b[5m',
  reverse: '\x1b[7m',
  hidden: '\x1b[8m',
  
  black: '\x1b[30m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  
  bgBlack: '\x1b[40m',
  bgRed: '\x1b[41m',
  bgGreen: '\x1b[42m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
  bgMagenta: '\x1b[45m',
  bgCyan: '\x1b[46m',
  bgWhite: '\x1b[47m'
};

// Вывод заголовка
console.log(`
${colors.bright}${colors.cyan}╔════════════════════════════════════════════════════╗
║                                                    ║
║               DRILL FLOW BOT SETUP                 ║
║                                                    ║
╚════════════════════════════════════════════════════╝${colors.reset}
`);

// Функция для выполнения команд с выводом логов
function runCommand(command, args, cwd = process.cwd()) {
  return new Promise((resolve, reject) => {
    console.log(`${colors.yellow}> Выполняю команду: ${colors.bright}${command} ${args.join(' ')}${colors.reset}`);
    
    const proc = spawn(command, args, { 
      cwd, 
      stdio: 'inherit',
      shell: process.platform === 'win32'
    });
    
    proc.on('close', (code) => {
      if (code === 0) {
        console.log(`${colors.green}✓ Команда успешно выполнена${colors.reset}`);
        resolve();
      } else {
        console.error(`${colors.red}✗ Ошибка выполнения команды (код ${code})${colors.reset}`);
        reject(new Error(`Command failed with code ${code}`));
      }
    });
    
    proc.on('error', (err) => {
      console.error(`${colors.red}✗ Не удалось выполнить команду: ${err.message}${colors.reset}`);
      reject(err);
    });
  });
}

// Проверка наличия .env файла
function checkEnvFile() {
  const envPath = path.join(process.cwd(), '.env');
  
  if (fs.existsSync(envPath)) {
    console.log(`${colors.green}✓ Файл .env найден${colors.reset}`);
    return Promise.resolve(true);
  } else {
    console.log(`${colors.yellow}! Файл .env не найден. Создаю...${colors.reset}`);
    
    return new Promise((resolve) => {
      rl.question(`${colors.cyan}Введите токен вашего Telegram бота (или оставьте пустым для использования тестового токена): ${colors.reset}`, (token) => {
        const botToken = token.trim() || '7293247588:AAH5qQkNUmhoTzZ-_MSw0gS4BKlSTAW5qdM';
        
        const envContent = `# Токен Telegram бота
TELEGRAM_TOKEN=${botToken}

# URL для вебхука в продакшене
WEBHOOK_URL=https://drilling-flow.vercel.app/api/webhook

# Порт для локального сервера
PORT=3000

# Режим разработки для отображения подробных ошибок
NODE_ENV=development`;
        
        fs.writeFileSync(envPath, envContent);
        console.log(`${colors.green}✓ Файл .env создан${colors.reset}`);
        resolve(true);
      });
    });
  }
}

// Установка зависимостей
async function installDependencies() {
  console.log(`\n${colors.cyan}${colors.bright}[1/4] Проверка зависимостей${colors.reset}`);
  
  try {
    await runCommand('npm', ['install']);
    return true;
  } catch (error) {
    console.error(`${colors.red}Ошибка установки зависимостей: ${error.message}${colors.reset}`);
    return false;
  }
}

// Запуск тестов для проверки работоспособности
async function runTests() {
  console.log(`\n${colors.cyan}${colors.bright}[2/4] Запуск тестов${colors.reset}`);
  
  try {
    await runCommand('node', ['test_bot_commands.js', '--test-mode']);
    return true;
  } catch (error) {
    console.error(`${colors.red}Тесты завершились с ошибкой: ${error.message}${colors.reset}`);
    return false;
  }
}

// Запуск локального сервера
function startServer() {
  console.log(`\n${colors.cyan}${colors.bright}[3/4] Запуск локального сервера${colors.reset}`);
  
  return new Promise((resolve) => {
    rl.question(`${colors.yellow}Хотите запустить сервер сейчас? (y/n): ${colors.reset}`, async (answer) => {
      if (answer.toLowerCase() === 'y' || answer.toLowerCase() === 'yes' || answer === '') {
        console.log(`${colors.green}Запускаю сервер...${colors.reset}`);
        
        try {
          await runCommand('npm', ['start']);
        } catch (error) {
          console.error(`${colors.red}Ошибка запуска сервера: ${error.message}${colors.reset}`);
        }
      } else {
        console.log(`${colors.yellow}Пропускаю запуск сервера.${colors.reset}`);
      }
      
      resolve(true);
    });
  });
}

// Отображение справки и завершение
function showHelp() {
  console.log(`\n${colors.cyan}${colors.bright}[4/4] Справка${colors.reset}`);
  
  console.log(`
${colors.bright}Настройка завершена!${colors.reset}

${colors.yellow}Доступные команды:${colors.reset}
  ${colors.green}npm start${colors.reset}              - Запуск локального сервера
  ${colors.green}npm run dev${colors.reset}            - Запуск в режиме разработки (с автоперезагрузкой)
  ${colors.green}npm run test:commands${colors.reset}  - Тестирование команд бота
  ${colors.green}npm run test:callbacks${colors.reset} - Тестирование callback-запросов

${colors.yellow}Документация:${colors.reset}
  Полную документацию можно найти в файле README.md
  
${colors.yellow}Конфигурация:${colors.reset}
  Настройки бота находятся в файле .env
  
${colors.bright}${colors.cyan}Спасибо за использование DrillFlow Bot!${colors.reset}
`);

  rl.close();
}

// Главная функция
async function main() {
  try {
    await checkEnvFile();
    if (await installDependencies()) {
      await startServer();
      showHelp();
    }
  } catch (error) {
    console.error(`${colors.red}${colors.bright}Произошла ошибка в процессе установки: ${error.message}${colors.reset}`);
    process.exit(1);
  }
}

// Запуск главной функции
main(); 