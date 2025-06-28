import React, { useEffect, useRef, useState, useCallback } from 'react';
import './App.css';
import './gh-pages-override.css'; // Создайте этот файл

export default function App() {
  const canvasRef = useRef(null);
  const ctxRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [color, setColor] = useState('#000000');
  const [brushSize, setBrushSize] = useState(5);

  // Удаление элементов GitHub Pages
  useEffect(() => {
    const removeGitHubElements = () => {
      const selectors = [
        '.footer', 
        '.ribbon',
        '.btn', 
        '.Header', 
        '.pagehead',
        '.octotree-show'
      ];
      
      selectors.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => el.remove());
      });
      
      document.body.style.padding = '0';
      document.body.style.margin = '0';
      document.documentElement.style.overflow = 'hidden';
    };

    removeGitHubElements();
    const timer = setTimeout(removeGitHubElements, 1500);
    
    return () => clearTimeout(timer);
  }, []);

  // Инициализация Telegram WebApp
  useEffect(() => {
    if (window.Telegram?.WebApp) {
      window.Telegram.WebApp.ready();
      window.Telegram.WebApp.expand();
      window.Telegram.WebApp.setHeaderColor('#ffffff');
      window.Telegram.WebApp.setBackgroundColor('#ffffff');
    }
  }, []);

  // Инициализация Canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    ctxRef.current = ctx;

    const resizeCanvas = () => {
      const devicePixelRatio = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      
      canvas.width = rect.width * devicePixelRatio;
      canvas.height = rect.height * devicePixelRatio;
      canvas.style.width = `${rect.width}px`;
      canvas.style.height = `${rect.height}px`;
      
      ctx.scale(devicePixelRatio, devicePixelRatio);
      updateDrawingParams();
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, []);

  // Обновление параметров рисования
  const updateDrawingParams = useCallback(() => {
    if (!ctxRef.current) return;
    
    ctxRef.current.strokeStyle = color;
    ctxRef.current.lineWidth = brushSize;
    ctxRef.current.lineCap = 'round';
    ctxRef.current.lineJoin = 'round';
  }, [color, brushSize]);

  useEffect(() => {
    updateDrawingParams();
  }, [color, brushSize, updateDrawingParams]);

  const startDrawing = (e) => {
    if (!ctxRef.current) return;
    
    setIsDrawing(true);
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches[0].clientX) - rect.left;
    const y = (e.clientY || e.touches[0].clientY) - rect.top;
    
    ctxRef.current.beginPath();
    ctxRef.current.moveTo(x, y);
  };

  const draw = (e) => {
    if (!isDrawing || !ctxRef.current) return;
    
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches[0].clientX) - rect.left;
    const y = (e.clientY || e.touches[0].clientY) - rect.top;
    
    ctxRef.current.lineTo(x, y);
    ctxRef.current.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    if (ctxRef.current) ctxRef.current.closePath();
  };

  const clearCanvas = () => {
    if (!canvasRef.current || !ctxRef.current) return;
    
    const canvas = canvasRef.current;
    ctxRef.current.clearRect(0, 0, canvas.width, canvas.height);
  };

  const sendToTelegram = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    canvas.toBlob((blob) => {
      if (window.Telegram?.WebApp) {
        const reader = new FileReader();
        reader.onload = () => {
          window.Telegram.WebApp.sendData(JSON.stringify({
            image: reader.result,
            userId: window.Telegram.WebApp.initDataUnsafe.user?.id
          }));
        };
        reader.readAsDataURL(blob);
      }
    }, 'image/png');
  };

  return (
    <div className="app">
      <h1>Открытка насте высылатель</h1>
      
      <canvas
        ref={canvasRef}
        className="canvas"
        onMouseDown={startDrawing}
        onMouseMove={draw}
        onMouseUp={stopDrawing}
        onMouseLeave={stopDrawing}
        onTouchStart={(e) => {
          e.preventDefault();
          startDrawing(e.touches[0]);
        }}
        onTouchMove={(e) => {
          e.preventDefault();
          draw(e.touches[0]);
        }}
        onTouchEnd={stopDrawing}
      />
      
      <div className="controls">
        <div className="color-picker">
          {['#000000', '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ffffff'].map((c) => (
            <button
              key={c}
              className="color-btn"
              style={{ 
                backgroundColor: c,
                transform: color === c ? 'scale(1.2)' : 'scale(1)',
                border: color === c ? '2px solid #333' : '1px solid #999'
              }}
              onClick={() => setColor(c)}
              aria-label={`Color ${c}`}
            />
          ))}
        </div>
        
        <div className="size-picker">
          {[5, 10, 30].map((size) => (
            <button
              key={size}
              style={{
                fontWeight: brushSize === size ? 'bold' : 'normal',
                backgroundColor: brushSize === size ? '#007bff' : '#f0f0f0',
                color: brushSize === size ? 'white' : '#333'
              }}
              onClick={() => setBrushSize(size)}
            >
              {size}рх ура!
            </button>
          ))}
        </div>
        
        <div className="actions">
          <button onClick={clearCanvas}>Очистить</button>
          <button onClick={sendToTelegram}>Отправить</button>
        </div>
      </div>
    </div>
  );
}