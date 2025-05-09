import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './InsectDetail.css';

const InsectDetail = () => {
  const { insectId } = useParams();
  const navigate = useNavigate();
  const [insectData, setInsectData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchInsectData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/insects/${insectId}`);
        
        if (!response.ok) {
          throw new Error('해충 정보를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        setInsectData(data);
      } catch (error) {
        console.error('데이터 불러오기 실패:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchInsectData();
  }, [insectId]);

  const handleBackClick = () => {
    navigate(-1);
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!insectData) {
    return <div className="error">해충 정보를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="insect-detail">
      <button className="back-button" onClick={handleBackClick}>← 이전으로</button>
      
      <div className="insect-info-card">
        <div className="insect-info-text">
          <h2 className="insect-title">{insectData.insectSpeciesKor || '해충 정보 없음'}</h2>
          <div className="insect-details">
            <h3>해충 정보</h3>
            <p><strong>해충명:</strong> {insectData.insectSpeciesKor || '정보 없음'}</p>
            <p><strong>생태정보:</strong> {insectData.ecologyInfo || '정보 없음'}</p>
            <p><strong>피해정보:</strong> {insectData.damageInfo || '정보 없음'}</p>
            <p><strong>방제방법:</strong> {insectData.preventMethod || '정보 없음'}</p>
            <p><strong>검역정보:</strong> {insectData.qrantInfo || '정보 없음'}</p>
            <p><strong>분포정보:</strong> {insectData.distrbInfo || '정보 없음'}</p>
            <p><strong>형태정보:</strong> {insectData.stleInfo || '정보 없음'}</p>
          </div>
        </div>
      </div>

      {insectData.spcsPhotoData && insectData.spcsPhotoData.length > 0 && (
        <div className="insect-images">
          <h3>해충 이미지</h3>
          <div className="image-grid">
            {insectData.spcsPhotoData.map((photo, index) => (
              <img
                key={index}
                src={photo.image}
                alt={insectData.insectSpeciesKor}
                className="insect-image"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InsectDetail; 