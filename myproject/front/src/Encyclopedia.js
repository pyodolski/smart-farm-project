import React from 'react';
import { useNavigate } from 'react-router-dom';
import './Encyclopedia.css';

// 더미 데이터
const crops = [
  {
    id: 'strawberry',
    name: '딸기',
    image: 'https://cdn.pixabay.com/photo/2018/04/29/11/54/strawberries-3359755_1280.jpg',
  },
  {
    id: 'tomato',
    name: '완숙 토마토',
    image: 'https://cdn.pixabay.com/photo/2016/03/26/16/44/tomatoes-1280859_1280.jpg',
  }
];

function Encyclopedia() {
  const navigate = useNavigate();

  const handleCropClick = (cropId) => {
    navigate(`/encyclopedia/${cropId}`);
  };

  return (
    <div className="encyclopedia-container">
      <div className="encyclopedia-header">
        <h1>작물 도감</h1>
        <p>다양한 작물들의 재배 정보와 병충해 정보를 확인하세요</p>
      </div>
      
      <div className="crop-cards">
        {crops.map(crop => (
          <div 
            key={crop.id} 
            className="crop-card" 
            onClick={() => handleCropClick(crop.id)}
          >
            <div className="crop-image-container">
              <img src={crop.image} alt={crop.name} className="crop-list-image" />
            </div>
            <div className="crop-info">
              <h2>{crop.name}</h2>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Encyclopedia; 