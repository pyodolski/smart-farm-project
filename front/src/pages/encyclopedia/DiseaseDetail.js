import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './DiseaseDetail.css';
import API_BASE_URL from '../../utils/config';

const DiseaseDetail = () => {
  const { diseaseId } = useParams();
  const navigate = useNavigate();
  const [diseaseData, setDiseaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const convertHtmlToText = (html) => {
    if (!html) return '정보 없음';
    return html.replace(/<br\s*\/?>/g, '\n');
  };

  useEffect(() => {
    const fetchDiseaseData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/diseases/${diseaseId}`, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('병해 정보를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        setDiseaseData(data);
      } catch (error) {
        console.error('데이터 불러오기 실패:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDiseaseData();
  }, [diseaseId]);

  const handleBackClick = () => {
    navigate(-1);
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!diseaseData) {
    return <div className="error">병해 정보를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="disease-detail">
      <button className="back-button" onClick={handleBackClick}>← 이전으로</button>
      
      <div className="disease-info-card">
        <div className="disease-info-text">
          <h2 className="disease-title">{diseaseData.sickNameKor}</h2>
          <div className="disease-details">
            <h3>병해 정보</h3>
            <p><strong>병명:</strong> {diseaseData.sickNameKor}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>전파 경로:</strong> {convertHtmlToText(diseaseData.developmentCondition)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>예방법:</strong> {convertHtmlToText(diseaseData.preventionMethod)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>증상:</strong> {convertHtmlToText(diseaseData.symptoms)}</p>
          </div>
        </div>
      </div>

      {diseaseData.imageList && diseaseData.imageList.length > 0 && (
        <div className="disease-images">
          <h3>병해 이미지</h3>
          <div className="image-grid">
            {diseaseData.imageList.map((image, index) => (
              <img
                key={index}
                src={image.image}
                alt={image.imageTitle || diseaseData.sickNameKor}
                className="disease-image"
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiseaseDetail; 