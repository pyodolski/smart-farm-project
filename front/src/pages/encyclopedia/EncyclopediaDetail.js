import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './EncyclopediaDetail.css';
import '../../styles/common.css';
import API_BASE_URL from '../../utils/config';

const cropImages = {
  'strawberry': 'https://cdn.pixabay.com/photo/2018/04/29/11/54/strawberries-3359755_1280.jpg',
  'tomato': 'https://cdn.pixabay.com/photo/2016/03/26/16/44/tomatoes-1280859_1280.jpg',
};

const EncyclopediaDetail = () => {
  const {crop} = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [cropData, setCropData] = useState(null);
  const [diseases, setDiseases] = useState([]);
  const [insects, setInsects] = useState([]);
  const [enemies, setEnemies] = useState([]);
  const [cropName, setCropName] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    const getCropNameKor = (id) => {
      const cropMap = {
        'strawberry': '딸기',
        'tomato': '완숙 토마토'
      };
      return cropMap[id] || id;
    };

    const fetchCropData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/api/crops/detail/${crop}`, {
          credentials: 'include'
        });
        
        if (!response.ok) {
          console.error(`API 응답 오류: ${response.status}`);
          throw new Error(`${crop}에 대한 정보를 불러올 수 없습니다.`);
        }
        
        const data = await response.json();
        console.log('API 응답 데이터:', data);

        setCropData({
          season: data.info.season,
          temp: data.info.temp,
          humidity: data.info.humidity
        });
        
        setDiseases(data.items || []);
        setInsects(data.insects || []);
        setEnemies(data.enemies || []);
        setCropName(getCropNameKor(crop));

      } catch (error) {
        console.error('데이터 불러오기 실패:', error);
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchCropData();
  }, [crop]);


  const handleDiseaseClick = (diseaseId) => {
    navigate(`/encyclopedia/disease/${diseaseId}`);
  };

  const handleInsectClick = (insectId) => {
    navigate(`/encyclopedia/insect/${insectId}`);
  };

  const handleEnemyClick = (enemyId) => {
    navigate(`/encyclopedia/enemy/${enemyId}`);
  };

  const handleBackClick = () => {
    navigate('/encyclopedia');
  };

  if(loading) {
    return <div className="loading">로딩 중</div>;
  }

  if(!cropData) {
    return <div className="error">작물 정보를 찾을 수 없습니다.</div>;
  }

  return(
    <div className="encyclopedia-detail">
      <button className="back-button" onClick={handleBackClick}>← 도감목록으로</button>
      <div className="crop-info-card">
        <img
          className="crop-image"
          src={cropImages[crop]}
          alt={cropName}
        />
        <div className="crop-info-text">
          <h2 className="crop-title">{cropName}</h2>
          <ul className="crop-info-list">
            <li><strong>재배 시기:</strong> {cropData.season}</li>
            <li><strong>적정 온도:</strong> {cropData.temp}℃</li>
            <li><strong>적정 습도:</strong> {cropData.humidity}%</li>
          </ul>
        </div>
      </div>
      
      {error && <div className="error-message">
        <p>{error}</p>
        <p>기본 데이터를 표시합니다.</p>
      </div>}
      
      <div className="card">
        <h2>병해 목록</h2>
        <div className="card-grid">
          {diseases.length > 0 ? (
            diseases.map((disease) => (
              <div 
                key={disease.sickKey} 
                className="card-item"
                onClick={() => handleDiseaseClick(disease.sickKey)}
              >
                <img src={disease.thumbImg} alt={disease.sickNameKor} />
                <p>{disease.sickNameKor}</p>
              </div>
            ))
          ): 
          (
            <p>병해 정보가 없습니다.</p>
          )}
        </div>
      </div>
      
      <div className="card">
        <h2>해충 피해</h2>
        <div className="card-grid">
          {insects.length > 0 ? (
            insects.map((insect) => (
              <div 
                key={insect.insectKey} 
                className="card-item"
                onClick={() => handleInsectClick(insect.insectKey)}
              >
                <img src={insect.thumbImg} alt={insect.insectKorName} />
                <p>{insect.insectKorName}</p>
              </div>
            ))
          ): 
          (
            <p>해충 정보가 없습니다.</p>
          )}
        </div>
      </div>

      <div className="card">
        <h2>천적 곤충</h2>
        <div className="card-grid">
          {enemies.length > 0 ? (
            enemies.map((enemy) => (
              <div 
                key={enemy.insectKey} 
                className="card-item"
                onClick={() => handleEnemyClick(enemy.insectKey)}
              >
                <img src={enemy.thumbImg} alt={enemy.insectSpeciesKor} />
                <p>{enemy.insectSpeciesKor}</p>
              </div>
            ))
          ): 
          (
            <p>천적 곤충 정보가 없습니다.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default EncyclopediaDetail;



