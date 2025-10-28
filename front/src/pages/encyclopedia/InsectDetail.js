import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './InsectDetail.css';
import API_BASE_URL from '../../utils/config';

const InsectDetail = () => {
  const { insectId } = useParams();
  const navigate = useNavigate();
  const [insectData, setInsectData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const convertHtmlToText = (html) => {
    if (!html) return '정보 없음';
    return html.replace(/<br\s*\/?>/g, '\n');
  };

  useEffect(() => {
    const fetchInsectData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/insects/${insectId}`, {
          credentials: 'include'
        });
        
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
            <p style={{ whiteSpace: 'pre-line' }}><strong>생태정보:</strong> {convertHtmlToText(insectData.ecologyInfo)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>피해정보:</strong> {convertHtmlToText(insectData.damageInfo)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>방제방법:</strong> {convertHtmlToText(insectData.preventMethod)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>검역정보:</strong> {convertHtmlToText(insectData.qrantInfo)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>분포정보:</strong> {convertHtmlToText(insectData.distrbInfo)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>형태정보:</strong> {convertHtmlToText(insectData.stleInfo)}</p>
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