import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from './contexts/AuthContext';
import './MainPage.css';
import { useNavigate } from 'react-router-dom';

// 별도의 모달 컴포넌트
function FarmModal({ show, onClose, title, onSubmit, initialData }) {
  const [localFormData, setLocalFormData] = useState({ name: '', location: '' });

  // 모달이 열릴 때 초기 데이터 설정
  useEffect(() => {
    if (show && initialData) {
      setLocalFormData(initialData);
    } else if (show) {
      setLocalFormData({ name: '', location: '' });
    }
  }, [show, initialData]);

  const handleLocalInputChange = (e) => {
    const { name, value } = e.target;
    setLocalFormData({
      ...localFormData,
      [name]: value
    });
  };
  //첨부파일용 변경버전
  const handleFormSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', localFormData.name);
    formData.append('location', localFormData.location);
    //formData.append('area', localFormData.area);
    formData.append('document', localFormData.document); // ← 핵심
  
    onSubmit(formData); // ← FormData 객체로 넘김
  };

  //const handleFormSubmit = (e) => {
  //  e.preventDefault();
  //  onSubmit(localFormData);
  //};

  if (!show) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2>{title}</h2>
        <form onSubmit={handleFormSubmit}>
          <div className="form-group">
            <label htmlFor="name">농장 이름:</label>
            <input
              id="name"
              name="name"
              type="text"
              value={localFormData.name}
              onChange={handleLocalInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="location">위치:</label>
            <input
              id="location"
              name="location"
              type="text"
              value={localFormData.location}
              onChange={handleLocalInputChange}
              required
            />
          </div>
          {!initialData && ( //변경사항
            <div className="form-group">
              <label htmlFor="document">농장주 증명 서류:</label>
              <input
                id="document"
                name="document"
                type="file"
                onChange={(e) =>
                  setLocalFormData({
                    ...localFormData,
                    document: e.target.files[0],
                  })
                }
                required
              />
            </div>
          )}
          <div className="modal-buttons">
            <button type="submit" className="submit-button">저장</button>
            <button type="button" onClick={onClose} className="cancel-button">취소</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function MainPage() {
  const [farms, setFarms] = useState([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [isLoggedIn] = useContext(AuthContext);
  const [weather, setWeather] = useState(null);
  const [twoDay, setTwoDay] = useState([]);
  const [selectedCity, setSelectedCity] = useState('서울특별시');
  const cities = [
    '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시',
    '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도',
    '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'
  ];
  const navigate = useNavigate();

  // 농장 목록 불러오기
  useEffect(() => {
    if (isLoggedIn) {
      fetchFarms();
    }
  }, [isLoggedIn]);

  useEffect(() => {
    fetch(`/api/weather?city=${selectedCity}`)
      .then(res => res.json())
      .then(data => {
        setWeather(data.weather);
        setTwoDay(data.two_day);
      });
  }, [selectedCity]);

  const fetchFarms = async () => {
    try {
      const response = await fetch('https://mature-grub-climbing.ngrok-free.app/api/farms', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setFarms(data.farms);
      }
    } catch (error) {
      console.error('농장 목록 불러오기 실패:', error);
    }
  };

  // 농장 추가
  const handleAddFarm = async (formData) => {
    try {
      const response = await fetch('https://mature-grub-climbing.ngrok-free.app/api/farms', {
        method: 'POST',
        //headers: {
        //  'Content-Type': 'application/json',
        //},
        //credentials: 'include',
        //body: JSON.stringify(formData)
        //변경 내용 >
        credentials: 'include',
        body: formData  // ← FormData 그대로 사용!
      });

      if (response.ok) {
        await fetchFarms();
        setShowAddModal(false);
      }
    } catch (error) {
      console.error('농장 추가 실패:', error);
    }
  };

  // 농장 수정
  const handleEditFarm = async (formData) => {
    try {
      const response = await fetch(`https://mature-grub-climbing.ngrok-free.app/api/farms/${selectedFarm.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        await fetchFarms();
        setShowEditModal(false);
        setSelectedFarm(null);
      }
    } catch (error) {
      console.error('농장 수정 실패:', error);
    }
  };

  // 농장 삭제
  const handleDeleteFarm = async (farmId) => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      try {
        const response = await fetch(`https://mature-grub-climbing.ngrok-free.app/api/farms/${farmId}`, {
          method: 'DELETE',
          credentials: 'include'
        });

        if (response.ok) {
          await fetchFarms();
        }
      } catch (error) {
        console.error('농장 삭제 실패:', error);
      }
    }
  };

  const openAddModal = () => {
    setShowAddModal(true);
  };

  const closeAddModal = () => {
    setShowAddModal(false);
  };

  const openEditModal = (farm) => {
    setSelectedFarm(farm);
    setShowEditModal(true);
  };

  const closeEditModal = () => {
    setShowEditModal(false);
    setSelectedFarm(null);
  };

  function weatherIcon(description) {
    if (!description) return '🌤️';
    const desc = description.toLowerCase();
    if (desc.includes('비')) return '🌧️';
    if (desc.includes('눈')) return '❄️';
    if (desc.includes('구름')) return '☁️';
    if (desc.includes('맑')) return '☀️';
    if (desc.includes('흐림')) return '🌥️';
    if (desc.includes('번개')) return '⛈️';
    if (desc.includes('안개')) return '🌫️';
  }

  return (
    <div className="mainpage-layout">
      <aside className="weather-aside">
        <div className="weather-card">
          <div className="weather-header">
            <h3>오늘의 날씨</h3>
            <select
              className="city-select"
              value={selectedCity}
              onChange={e => setSelectedCity(e.target.value)}
            >
              {cities.map(city => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>
          {weather && (
            <div className="weather-today">
              <div className="weather-icon">{weatherIcon(weather.description)}</div>
              <div className="weather-info">
                <div className="weather-temp">{weather.temperature}°C</div>
                <div className="weather-desc">{weather.description}</div>
              </div>
            </div>
          )}
          <div className="weather-forecast-title">내일/모레 예보</div>
          <div className="weather-forecast-row">
            {twoDay.map(day => (
              <div className="forecast-card" key={day.date}>
                <div className="forecast-date">{day.date}</div>
                <div className="forecast-temp">{day.min_temp}°C ~ {day.max_temp}°C</div>
                <div className="forecast-desc">{day.description} {weatherIcon(day.description)}</div>
              </div>
            ))}
          </div>
        </div>
      </aside>
      

      <main className="main-content">
        <h1>내 농장 목록</h1>
        <p>농장을 추가하거나 관리하세요</p>
        {!isLoggedIn ? (
          <div className="empty-farm-message">
            <p>등록된 농장이 없습니다.</p>
          </div>
        ) : (
          <div className="farm-list">
            {farms.length === 0 ? (
              <div className="empty-farm-box" onClick={openAddModal}>
                <span className="plus-icon">+</span>
                <p>등록된 농장이 없습니다.</p>
              </div>
            ) : (
              <div className="farms-grid">
                {farms.map((farm) => (
                  <div
                    key={farm.id}
                    className="farm-card"
                    onClick={() => navigate(`/farm-card-tail/${farm.id}`)}
                    style={{ cursor: 'pointer' }}
                  >
                    <h3>{farm.name}</h3>
                    <p>위치: {farm.location}</p>
                    <div className="farm-buttons" onClick={e => e.stopPropagation()}>
                      <button onClick={() => openEditModal(farm)}>수정</button>
                      <button onClick={() => handleDeleteFarm(farm.id)}>삭제</button>
                    </div>
                  </div>
                ))}
                <div className="add-farm-card" onClick={openAddModal}>
                  <span className="plus-icon">+</span>
                  <p>농장 추가</p>
                </div>
              </div>
            )}
          </div>
        )}
        {/* 추가/수정 모달 */}
        <FarmModal 
          show={showAddModal}
          onClose={closeAddModal}
          title="농장 추가"
          onSubmit={handleAddFarm}
          initialData={null}
        />
        <FarmModal
          show={showEditModal}
          onClose={closeEditModal}
          title="농장 수정"
          onSubmit={handleEditFarm}
          initialData={selectedFarm}
        />
      </main>
    </div>
  );
}

export default MainPage;