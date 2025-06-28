// Инициализация элементов
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const toast = document.getElementById('toast');
let isDrawing = false;
let currentColor = '#000000';
let currentSize = 5;

// Показ уведомления
function showToast(message, duration = 2000) {
  toast.textContent = message;
  toast.style.opacity = 1;
  setTimeout(() => toast.style.opacity = 0, duration);
}

// Корректная инициализация Canvas с учётом DPI
function initCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpi = window.devicePixelRatio || 1;
  
  // Устанавливаем физические размеры
  canvas.width = rect.width * dpi;
  canvas.height = rect.height * dpi;
  
  // Устанавливаем отображаемые размеры
  canvas.style.width = `${rect.width}px`;
  canvas.style.height = `${rect.height}px`;
  
  // Масштабируем контекст
  ctx.scale(dpi, dpi);
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = currentColor;
  ctx.lineWidth = currentSize;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';
}

// Получение координат с учётом DPI
function getPosition(e) {
  const rect = canvas.getBoundingClientRect();
  const touch = e.touches ? e.touches[0] : e;
  return {
    x: (touch.clientX - rect.left) * (canvas.width / rect.width / window.devicePixelRatio),
    y: (touch.clientY - rect.top) * (canvas.height / rect.height / window.devicePixelRatio)
  };
}

// Обработчики рисования
function startDrawing(e) {
  isDrawing = true;
  const pos = getPosition(e);
  ctx.beginPath();
  ctx.moveTo(pos.x, pos.y);
  e.preventDefault();
}

function draw(e) {
  if (!isDrawing) return;
  const pos = getPosition(e);
  ctx.lineTo(pos.x, pos.y);
  ctx.stroke();
  e.preventDefault();
}

function stopDrawing() {
  isDrawing = false;
}

// Инициализация инструментов
document.querySelectorAll('.color-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentColor = btn.dataset.color;
    ctx.strokeStyle = currentColor;
  });
});

document.querySelectorAll('.size-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentSize = parseInt(btn.dataset.size);
    ctx.lineWidth = currentSize;
  });
});

// Очистка холста
document.getElementById('clear-btn').addEventListener('click', () => {
  ctx.fillStyle = 'white';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  showToast('Холст очищен');
});

// Функция скачивания (теперь работает на iOS с сохранением в фотопленку)
document.getElementById('download-btn').addEventListener('click', async () => {
    try {
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = canvas.width;
      tempCanvas.height = canvas.height;
      const tempCtx = tempCanvas.getContext('2d');
      
      tempCtx.fillStyle = 'white';
      tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
      tempCtx.drawImage(canvas, 0, 0);
      
      // Конвертируем в Blob
      tempCanvas.toBlob(async (blob) => {
        // Альтернативный вариант для iOS
    if (/iPhone|iPad|iPod/i.test(navigator.userAgent)) {
        const link = document.createElement('a');
        link.href = imageBase64; // data:image/jpeg;base64,...
        link.download = 'граффити.jpg';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
  } else {
          // Стандартное скачивание для других устройств
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `граффити_${new Date().toLocaleDateString()}.jpg`;
          document.body.appendChild(a);
          a.click();
          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }, 100);
        }
        showToast('Изображение сохранено');
      }, 'image/jpeg', 0.9);
    } catch (error) {
      console.error('Ошибка скачивания:', error);
      showToast('Ошибка при сохранении', 3000);
    }
  });
  
  // Функция отправки (исправленная)
  document.getElementById('send-btn').addEventListener('click', async () => {
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    
    try {
      // Создаем JPEG изображение
      const tempCanvas = document.createElement('canvas');
      tempCanvas.width = canvas.width;
      tempCanvas.height = canvas.height;
      const tempCtx = tempCanvas.getContext('2d');
      
      tempCtx.fillStyle = 'white';
      tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
      tempCtx.drawImage(canvas, 0, 0);
      
      // Конвертируем в base64
      const imageBase64 = await new Promise(resolve => {
        tempCanvas.toBlob(blob => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        }, 'image/jpeg', 0.9);
      });
      
      // Отправка через Telegram WebApp
      if (window.Telegram?.WebApp) {
        Telegram.WebApp.sendData(JSON.stringify({ image: imageBase64 }));
        
        Telegram.WebApp.onEvent('webAppDataSendCompleted', () => {
          showToast('Успешно отправлено!');
          setTimeout(() => Telegram.WebApp.close(), 1000);
        });
        
        Telegram.WebApp.onEvent('webAppDataSendFailed', () => {
          showToast('Ошибка отправки', 3000);
          sendBtn.disabled = false;
        });
      } else {
        // Для отладки в браузере
        console.log('Имитация отправки:', { image: imageBase64 });
        showToast('В Telegram будет отправлено');
        sendBtn.disabled = false;
      }
    } catch (error) {
      console.error('Ошибка:', error);
      showToast('Ошибка при отправке', 3000);
      sendBtn.disabled = false;
    }
  });

// Инициализация
initCanvas();
window.addEventListener('resize', initCanvas);

// Обработчики событий
canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', draw);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);
canvas.addEventListener('touchstart', startDrawing, { passive: false });
canvas.addEventListener('touchmove', draw, { passive: false });
canvas.addEventListener('touchend', stopDrawing);

// Инициализация Telegram WebApp
if (window.Telegram?.WebApp) {
  Telegram.WebApp.ready();
  Telegram.WebApp.expand();
}