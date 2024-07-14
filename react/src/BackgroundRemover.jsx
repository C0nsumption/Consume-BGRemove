import React, { useState, useEffect, useRef } from 'react';

const BackgroundRemover = () => {
  const [inputImage, setInputImage] = useState(null);
  const [outputImage, setOutputImage] = useState(null);
  const [selectedColor, setSelectedColor] = useState(null);
  const [tolerance, setTolerance] = useState(30);
  const [blurRadius, setBlurRadius] = useState(2);
  const [mode, setMode] = useState('simple');
  const [refineEdges, setRefineEdges] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const canvasRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (inputImage) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      const img = new Image();
      img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0, img.width, img.height);
      };
      img.src = inputImage;
    }
  }, [inputImage]);

  useEffect(() => {
    if (selectedColor) {
      sendProcessingRequest();
    }
  }, [selectedColor, tolerance, blurRadius, mode, refineEdges]);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => setInputImage(e.target.result);
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('file', file);
    await fetch('http://localhost:8000/upload/', {
      method: 'POST',
      body: formData,
    });

    initWebSocket();
  };

  const initWebSocket = () => {
    wsRef.current = new WebSocket('ws://localhost:8000/ws');
    wsRef.current.onmessage = (event) => {
      const blob = new Blob([event.data], { type: 'image/png' });
      const url = URL.createObjectURL(blob);
      setOutputImage(url);
      setIsProcessing(false);
    };
  };

  const sendProcessingRequest = () => {
    if (!wsRef.current) return;
    setIsProcessing(true);
    const params = {
      tolerance,
      blur_radius: blurRadius,
      mode,
      refine: refineEdges,
      color: selectedColor
    };
    wsRef.current.send(JSON.stringify(params));
  };

  const handleCanvasClick = (event) => {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    const pixelData = ctx.getImageData(x, y, 1, 1).data;
    setSelectedColor(`${pixelData[0]},${pixelData[1]},${pixelData[2]}`);
  };

  return (
    <div className="background-remover">
      <h1>Background Remover</h1>
      <input type="file" onChange={handleFileUpload} className="file-input" />
      <div className="image-container">
        <div className="image-wrapper">
          {inputImage && (
            <canvas
              ref={canvasRef}
              onClick={handleCanvasClick}
              className="image-canvas"
            />
          )}
        </div>
        <div className="image-wrapper">
          {outputImage && <img src={outputImage} alt="Processed" className="output-image" />}
        </div>
      </div>
      <div className="controls">
        <label>
          Tolerance:
          <input
            type="range"
            min="0"
            max="100"
            value={tolerance}
            onChange={(e) => setTolerance(Number(e.target.value))}
          />
          {tolerance}
        </label>
        <label>
          Blur Radius:
          <input
            type="range"
            min="0"
            max="5"
            step="0.1"
            value={blurRadius}
            onChange={(e) => setBlurRadius(Number(e.target.value))}
          />
          {blurRadius.toFixed(1)}
        </label>
        <div>
          <label>
            <input
              type="radio"
              value="simple"
              checked={mode === 'simple'}
              onChange={() => setMode('simple')}
            />
            Simple
          </label>
          <label>
            <input
              type="radio"
              value="advanced"
              checked={mode === 'advanced'}
              onChange={() => setMode('advanced')}
            />
            Advanced
          </label>
        </div>
        <label>
          <input
            type="checkbox"
            checked={refineEdges}
            onChange={(e) => setRefineEdges(e.target.checked)}
          />
          Refine Edges
        </label>
      </div>
      {isProcessing && <p>Processing...</p>}
    </div>
  );
};

export default BackgroundRemover;
