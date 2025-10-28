import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './EnemyDetail.css';
import API_BASE_URL from '../../utils/config';

const EnemyDetail = () => {
  const { enemyId } = useParams();
  const navigate = useNavigate();
  const [enemyData, setEnemyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const convertHtmlToText = (html) => {
    if (!html) return '정보 없음';
    return html.replace(/<br\s*\/?>/g, '\n');
  };

  useEffect(() => {
    const fetchEnemyData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/enemies/${enemyId}`, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          throw new Error('천적 정보를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        setEnemyData(data);
      } catch (error) {
        console.error('데이터 불러오기 실패:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEnemyData();
  }, [enemyId]);

  const handleBackClick = () => {
    navigate(-1);
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!enemyData) {
    return <div className="error">천적 정보를 찾을 수 없습니다.</div>;
  }

  return (
    <div className="enemy-detail">
      <button className="back-button" onClick={handleBackClick}>← 이전으로</button>
      
      <div className="enemy-info-card">
        <div className="enemy-info-text">
          <h2 className="enemy-title">{enemyData.insectSpeciesKor || '천적 곤충 정보 없음'}</h2>
          <div className="enemy-details">
            <h3>천적 곤충 정보</h3>
            <p><strong>천적 곤충명:</strong> {enemyData.insectSpeciesKor || '정보 없음'}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>국내 분포:</strong> {convertHtmlToText(enemyData.domesticDistribution)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>특징:</strong> {convertHtmlToText(enemyData.feature)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>생활사:</strong> {convertHtmlToText(enemyData.lifeCycle)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>이용방법:</strong> {convertHtmlToText(enemyData.utilizationMethod)}</p>
            <p style={{ whiteSpace: 'pre-line' }}><strong>기타 작물:</strong> {convertHtmlToText(enemyData.etcCrop)}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnemyDetail; 