import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function FarmDetail() {
  const { farmId } = useParams();
  const [greenhouses, setGreenhouses] = useState([]);

  useEffect(() => {
    fetch(`/api/greenhouses/list/${farmId}`)
      .then((res) => res.json())
      .then((data) => {
        setGreenhouses(data.greenhouses);
      })
      .catch(() => alert('비닐하우스 목록 불러오기 실패'));
  }, [farmId]);

  const handleAddGreenhouse = () => {
  window.location.href = `http://localhost:5001/grid?farm_id=${farmId}`;
};


  const handleEditGreenhouse = (id) => {
    window.location.href = `http://localhost:5001/grid?id=${id}`;
    // Flask 쪽 라우트로 맞춰야 함
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
    <div style={{ display: 'flex', height: '100vh' }}>
      <div
        style={{
          width: '280px',
          backgroundColor: '#f7f7f7',
          borderRight: '1px solid #ddd',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '10px 20px',
          }}
        >
          {greenhouses.length === 0 && (
            <p style={{ color: '#999' }}>등록된 비닐하우스가 없습니다.</p>
          )}
          {greenhouses.map((gh) => (
            <div
              key={gh.id}
              style={{
                backgroundColor: '#fff',
                padding: '10px',
                marginBottom: '10px',
                border: '1px solid #ccc',
                borderRadius: '4px',
              }}
            >
              <div>{gh.name}</div>
              <div style={{ marginTop: '5px', display: 'flex', gap: '5px' }}>
                <button
                  onClick={() => handleEditGreenhouse(gh.id)}
                  style={{
                    fontSize: '12px',
                    backgroundColor: '#4CAF50',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '5px 10px',
                  }}
                >
                  수정
                </button>
                <button
                  onClick={() => handleDeleteGreenhouse(gh.id)}
                  style={{
                    fontSize: '12px',
                    backgroundColor: '#f44336',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    padding: '5px 10px',
                  }}
                >
                  삭제
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div
        style={{
          flex: 1,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#fff',
        }}
      >
        <button
          onClick={handleAddGreenhouse}
          style={{
            padding: '20px 40px',
            fontSize: '20px',
            cursor: 'pointer',
            backgroundColor: '#4CAF50',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
          }}
        >
          + 비닐하우스 추가
        </button>
      </div>
    </div>
  );
}

export default FarmDetail;
