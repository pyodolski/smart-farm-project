import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API_BASE_URL from '../../utils/config';
import './FarmDetail.css';

function FarmDetail() {
  const { farmId } = useParams();
  const [greenhouses, setGreenhouses] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [weather, setWeather] = useState({ temperature: null, description: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetch(`/api/greenhouses/list/${farmId}`)
      .then((res) => res.json())
      .then((data) => {
        console.log('Greenhouses API response:', data);
        const greenhousesData = data && data.greenhouses ? data.greenhouses : [];
        setGreenhouses(greenhousesData);
      })
      .catch(() => setGreenhouses([]));
  }, [farmId]);

  useEffect(() => {
    fetch(`/api/farms/${farmId}/weather`, {
      credentials: 'include'
    })
      .then(res => {
        if (!res.ok) throw new Error(`Status ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.log('Weather API response:', data);
        setWeather({
          temperature: data.temperature,
          description: data.description
        });
      })
      .catch(err => {
        console.error('날씨 조회 실패', err);
        setError('날씨 정보를 불러올 수 없습니다.');
      });
  }, [farmId]);

  const handleSidebarToggle = () => {
    setSidebarOpen((open) => !open);
  };

  const handleAddGreenhouse = () => {
    navigate(`/greenhouse-grid/${farmId}`);
  };

  const handleEditGreenhouse = (id) => {
    window.location.href = `${API_BASE_URL}/grid?id=${id}`;
  };

  const handleDeleteGreenhouse = (id) => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      fetch(`/api/greenhouses/delete/${id}`, {
        method: 'DELETE',
      })
        .then((res) => res.json())
        .then((data) => {
          alert(data.message);
          setGreenhouses(greenhouses.filter((gh) => gh.id !== id));
        })
        .catch(() => alert('삭제 중 오류 발생'));
    }
  };

  return (
    <div className="farmdetail-container">
      <aside className={`farmdetail-sidebar${sidebarOpen ? '' : ' closed'}`}>
        <div className="farmdetail-sidebar-header">
          <h3 className="farmdetail-sidebar-title">비닐하우스 목록</h3>
          <button
            className="farmdetail-sidebar-toggle"
            onClick={handleSidebarToggle}
            aria-label={sidebarOpen ? '사이드바 접기' : '사이드바 펴기'}
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>
        {sidebarOpen && (
          greenhouses.length === 0 ? (
            <p className="farmdetail-empty">등록된 비닐하우스가 없습니다.</p>
          ) : (
            <ul className="farmdetail-list">
              {greenhouses.map((gh) => (
                <li key={gh.id}>{gh.name}</li>
              ))}
            </ul>
          )
        )}
      </aside>
      <main className="farmdetail-main">
        <button
          onClick={handleAddGreenhouse}
          className="farmdetail-add-btn"
        >
          + 비닐하우스 추가
        </button>
      </main>
    </div>
  );
}

export default FarmDetail;
