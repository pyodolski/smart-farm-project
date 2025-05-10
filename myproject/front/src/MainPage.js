import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from './contexts/AuthContext';
import './MainPage.css';

// 별도의 모달 컴포넌트
function FarmModal({ show, onClose, title, onSubmit, initialData }) {
  const [localFormData, setLocalFormData] = useState({ name: '', location: '', area: '' });

  // 모달이 열릴 때 초기 데이터 설정
  useEffect(() => {
    if (show && initialData) {
      setLocalFormData(initialData);
    } else if (show) {
      setLocalFormData({ name: '', location: '', area: '' });
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
    formData.append('area', localFormData.area);
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
          <div className="form-group">
            <label htmlFor="area">면적 (㎡):</label>
            <input
              id="area"
              name="area"
              type="number"
              step="0.01"
              value={localFormData.area}
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

  // 농장 목록 불러오기
  useEffect(() => {
    if (isLoggedIn) {
      fetchFarms();
    }
  }, [isLoggedIn]);

  const fetchFarms = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/farms', {
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
      const response = await fetch('http://localhost:5001/api/farms', {
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
      const response = await fetch(`http://localhost:5001/api/farms/${selectedFarm.id}`, {
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
        const response = await fetch(`http://localhost:5001/api/farms/${farmId}`, {
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

  return (
    <div className="main-container">
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
                <div key={farm.id} className="farm-card">
                  <h3>{farm.name}</h3>
                  <p>위치: {farm.location}</p>
                  <p>면적: {farm.area} ㎡</p>
                  <div className="farm-buttons">
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

      {/* 추가 모달 */}
      <FarmModal 
        show={showAddModal}
        onClose={closeAddModal}
        title="농장 추가"
        onSubmit={handleAddFarm}
        initialData={null}
      />

      {/* 수정 모달 */}
      <FarmModal
        show={showEditModal}
        onClose={closeEditModal}
        title="농장 수정"
        onSubmit={handleEditFarm}
        initialData={selectedFarm}
      />
    </div>
  );
}

export default MainPage;