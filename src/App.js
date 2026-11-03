import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [productId, setProductId] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!productId.trim()) {
      setError('Please enter a product ID');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Сначала получаем список изображений для продукта
      const imagesResponse = await fetch(`http://localhost:5003/product-images/${productId.trim()}`);
      const imagesData = await imagesResponse.json();

      // Затем анализируем продукт
      const analyzeResponse = await fetch('http://localhost:5003/analyze-product', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId.trim() }),
      });

      const data = await analyzeResponse.json();

      if (!analyzeResponse.ok) {
        throw new Error(data.error || 'Failed to process product');
      }

      // Объединяем данные для отображения
      const combinedResults = {
        ...data,
        imagesInfo: imagesData
      };

      // Добавим отладочный вывод для проверки данных
      console.log('Combined results:', combinedResults);

      setResults(combinedResults);
    } catch (err) {
      setError(err.message || 'An error occurred while processing the request');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  // Компонент для отображения изображения с информацией о найденных объектах
  const ImageViewWithDetails = ({ imageInfo, imageFeatures, index }) => {
    // Debug function to check bounding box validity
    const isValidBoundingBox = (bbox) => {
      if (!bbox) return false;
      return typeof bbox.x_min === 'number' &&
             typeof bbox.y_min === 'number' &&
             typeof bbox.x_max === 'number' &&
             typeof bbox.y_max === 'number' &&
             bbox.x_min <= bbox.x_max &&
             bbox.y_min <= bbox.y_max;
    };

    // Функция для преобразования координат из 0-1000 в проценты
    const convertToPercentages = (bbox) => {
      if (!bbox) return null;

      // Убедимся, что значения находятся в пределах 0-1000
      const xMin = Math.max(0, Math.min(1000, bbox.x_min));
      const yMin = Math.max(0, Math.min(1000, bbox.y_min));
      const xMax = Math.max(0, Math.min(1000, bbox.x_max));
      const yMax = Math.max(0, Math.min(1000, bbox.y_max));

      // Преобразование в проценты
      const left = (xMin / 1000) * 100;
      const top = (yMin / 1000) * 100;
      const width = ((xMax - xMin) / 1000) * 100;
      const height = ((yMax - yMin) / 1000) * 100;

      return {
        left: left,
        top: top,
        width: width,
        height: height
      };
    };

    // Простая обёртка для отображения внешнего контейнера
    const renderBoundingBox = (obj, objIndex) => {
      if (!obj.bbox || !isValidBoundingBox(obj.bbox)) {
        // For debugging - log invalid bounding boxes
        console.log(`Invalid bounding box for object ${objIndex}:`, obj.bbox);
        return null;
      }

      const percentages = convertToPercentages(obj.bbox);
      if (!percentages) return null;

      return (
        <div
          key={objIndex}
          style={{
            position: 'absolute',
            left: `${percentages.left}%`,
            top: `${percentages.top}%`,
            width: `${percentages.width}%`,
            height: `${percentages.height}%`,
            border: '2px solid #4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            zIndex: 10,
            boxSizing: 'border-box',
            pointerEvents: 'none'  // Prevent interfering with image interaction
          }}
          className="bounding-box-overlay"
        >
          {obj.name && (
            <div
              style={{
                position: 'absolute',
                top: '-25px',
                left: '0',
                backgroundColor: '#4CAF50',
                color: 'white',
                padding: '2px 6px',
                fontSize: '12px',
                borderRadius: '2px',
                zIndex: 11,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '100%'
              }}
            >
              {obj.name}
            </div>
          )}
        </div>
      );
    };

    // Для корректной работы с изображениями, которые могут загружаться асинхронно
    const [imageLoaded, setImageLoaded] = useState(false);
    const [imageError, setImageError] = useState(false);

    // Добавим обработку ошибок и проверку наличия изображения
    const handleImageLoad = () => {
      setImageLoaded(true);
      setImageError(false);
    };

    const handleImageError = () => {
      setImageLoaded(true);
      setImageError(true);
    };

    // Проверим, что изображение загружено и есть данные для отображения
    const shouldRenderBoxes = imageLoaded && !imageError && imageFeatures && imageFeatures.length > 0;

    // Для отладки - добавим логирование
    useEffect(() => {
      if (imageFeatures) {
        console.log('Rendering boxes for image with features:', imageFeatures);
        console.log('Features structure:', JSON.stringify(imageFeatures, null, 2));
        
        // Проверка структуры
        if (!Array.isArray(imageFeatures)) {
          console.log('WARNING: imageFeatures is not an array:', typeof imageFeatures);
        } else if (imageFeatures.length === 0) {
          console.log('WARNING: imageFeatures is empty array');
        } else {
          console.log('First feature:', imageFeatures[0]);
          if (imageFeatures[0].highlights && Array.isArray(imageFeatures[0].highlights)) {
            console.log('Highlights count:', imageFeatures[0].highlights.length);
            console.log('First highlight:', imageFeatures[0].highlights[0]);
          }
          if (imageFeatures[0].bbox) {
            console.log('Direct bbox found:', imageFeatures[0].bbox);
          }
        }
      }
    }, [imageFeatures]);

    return (
      <div key={index} className="image-item">
        <div className="image-container" style={{ position: 'relative', display: 'inline-block' }}>
          {!imageError && (
            <img
              src={`http://localhost:5003/images/${imageInfo.filename}`}
              alt={`Product ${index + 1}`}
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{
                maxWidth: '100%',
                height: 'auto',
                display: 'block',
                position: 'relative'
              }}
            />
          )}

          {imageError && (
            <div style={{
              width: '300px',
              height: '300px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#333',
              color: 'white'
            }}>
              Image not found
            </div>
          )}

          {/* Визуализация bounding boxes */}
          {shouldRenderBoxes && imageFeatures.map((obj, objIndex) => {
            // Для отладки - проверим структуру данных
            console.log(`Processing object ${objIndex}:`, obj);

            // Обрабатываем каждый объект в highlights
            if (obj.highlights && obj.highlights.length > 0) {
              return obj.highlights.map((highlight, highlightIndex) =>
                renderBoundingBox(highlight, `${objIndex}-${highlightIndex}`)
              );
            }

            // Обрабатываем вариант, когда в objects есть bbox напрямую (возможная структура)
            if (obj.bbox) {
              return renderBoundingBox(obj, objIndex);
            }

            return null;
          })}
        </div>

        <div className="image-info">
          <p>Order: {imageInfo.order}</p>
          <p>Filename: {imageInfo.filename}</p>
          <p>Status: {imageInfo.exists ? '✓ Available' : '✗ Not Found'}</p>
        </div>

        {/* Отображаем информацию об объектах под изображением */}
        {imageFeatures && imageFeatures.length > 0 && (
          <div className="object-details">
            <h4>Detected Objects:</h4>
            {imageFeatures.map((obj, objIndex) => (
              <div key={objIndex} className="object-detail-item">
                <p><strong>Object {objIndex + 1}:</strong> {obj.name}</p>
                <p><strong>Location:</strong> {obj.location}</p>
                <p><strong>Size:</strong> {obj.size}</p>
                <p><strong>Bounding Box:</strong></p>
                <ul>
                  <li>x_min: {obj.bbox?.x_min}</li>
                  <li>y_min: {obj.bbox?.y_min}</li>
                  <li>x_max: {obj.bbox?.x_max}</li>
                  <li>y_max: {obj.bbox?.y_max}</li>
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Product Image Analyzer</h1>
        <div className="input-section">
          <input
            type="text"
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter product ID"
            className="product-id-input"
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="analyze-button"
          >
            {loading ? 'Analyzing...' : 'Analyze Product'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {results && (
          <div className="results-section">
            <h2>Analysis Results for Product {results.product_id}</h2>
            <p>Images processed: {results.images_processed}</p>

            <div className="images-grid">
              <h3>Product Images</h3>
              {results.imagesInfo?.images?.map((img, index) => {
                // Получаем данные для конкретного изображения
                const imageFeatures = results.features?.[index];
                return (
                  <ImageViewWithDetails
                    key={index}
                    imageInfo={img}
                    imageFeatures={imageFeatures}
                    index={index}
                  />
                );
              })}
            </div>

            <div className="analysis-results">
              <h3>Complete Object Analysis</h3>
              {results.features?.map((imageFeatures, imageIndex) => (
                <div key={imageIndex} className="image-analysis">
                  <h4>Image {imageIndex + 1} Detailed Analysis</h4>
                  {imageFeatures?.map((obj, objIndex) => (
                    <div key={objIndex} className="object-feature">
                      <h5>{obj.name}</h5>
                      <p><strong>Location:</strong> {obj.location}</p>
                      <p><strong>Size:</strong> {obj.size}</p>
                      <p><strong>Bounding Box Coordinates:</strong></p>
                      <ul>
                        <li>x_min: {obj.bbox?.x_min}</li>
                        <li>y_min: {obj.bbox?.y_min}</li>
                        <li>x_max: {obj.bbox?.x_max}</li>
                        <li>y_max: {obj.bbox?.y_max}</li>
                      </ul>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;