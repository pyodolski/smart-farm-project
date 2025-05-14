import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './EnemyDetail.css';

const EnemyDetail = () => {
  const { enemyId } = useParams();
  const navigate = useNavigate();
  const [enemyData, setEnemyData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchEnemyData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/enemies/${enemyId}`);
        
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
            <p><strong>국내 분포:</strong> {enemyData.domesticDistribution || '정보 없음'}</p>
            <p><strong>특징:</strong> {enemyData.feature || '정보 없음'}</p>
            <p><strong>생활사:</strong> {enemyData.lifeCycle || '정보 없음'}</p>
            <p><strong>이용방법:</strong> {enemyData.utilizationMethod || '정보 없음'}</p>
            <p><strong>기타 작물:</strong> {enemyData.etcCrop || '정보 없음'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnemyDetail; 