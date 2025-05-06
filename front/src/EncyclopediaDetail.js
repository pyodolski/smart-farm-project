import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './EncyclopediaDetail.css';

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

    const fetchCropData= async ()=> {
      try{
        setLoading(true);
        setCropName(getCropNameKor(crop));
        
        console.log(`작물 ID: ${crop}, 한글명: ${getCropNameKor(crop)}`);
        
        const response = await fetch(`/api/crops/detail/${crop}`);
        
        if(!response.ok) {
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
        
        setDiseases(data.items|| []);
        setInsects(data.insects|| []);
        setEnemies(data.enemies|| []);

      }catch(error) {
        console.error('데이터 불러오기 실패:', error);
        setError(error.message);

        const defaultData= getDefaultCropData(crop);
        setCropData(defaultData.info);
        setDiseases(defaultData.diseases);
        setInsects(defaultData.insects);
        setEnemies(defaultData.enemies);
        
      } finally {
        setLoading(false);
      }
    };

    fetchCropData();
  }, 
  [crop]);


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
      <button className="back-button" onClick={handleBackClick}>← 목록으로</button>
      
      <h1>{cropName} 재배 정보 및 병해충 목록</h1>
      
      {error && <div className="error-message">
        <p>{error}</p>
        <p>기본 데이터를 표시합니다.</p>
      </div>}
      
      {/* 작물 기본 정보 */}
      <div className="card">
        <h2>작물 재배 정보</h2>
        <ul>
          <li><strong>재배 시기:</strong> {cropData.season}</li>
          <li><strong>적정 온도:</strong> {cropData.temp}℃</li>
          <li><strong>적정 습도:</strong> {cropData.humidity}%</li>
        </ul>
      </div>

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



