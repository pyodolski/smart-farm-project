import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Products.css';
import API_BASE_URL from '../../utils/config';

function Products() {
  const [devices, setDevices] = useState([]);
  const navigate = useNavigate();

  const loadDevices = () => {
    fetch(`${API_BASE_URL}/product/my_devices`, {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        if (data.devices) {
          setDevices(data.devices);
        }
      })
      .catch(err => console.error("구독 목록 불러오기 실패:", err));
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleSubscribe = () => {
    navigate('/iot-setting');
  };

  const handleUnsubscribe = async (id) => {
    const confirmed = window.confirm("정말 구독을 취소하시겠습니까?");
    if (!confirmed) return;

    try {
      const res = await fetch(`${API_BASE_URL}/product/unsubscribe/${id}`, {
        method: "DELETE",
        credentials: "include"
      });
      const data = await res.json();
      alert(data.message);
      loadDevices();
    } catch (err) {
      alert("❌ 구독 취소 실패");
      console.error(err);
    }
  };

  return (
    <div className="products-flex-container">
      <div className="products-list-section">
        <h3 className="products-title">내 IOT 구독</h3>
        {devices.length === 0 ? (
          <p>아직 구독한 기기가 없습니다.</p>
        ) : (
          <ul className="products-list">
            {devices.map((device) => (
              <li key={device.id} className="products-list-item">
                <div className="products-list-header">
                  <span className="products-list-icon">📷</span>
                  <span className="products-list-name">{device.iot_name}</span>
                </div>
                <div className="products-list-btns">
                  <button
                    className="products-list-edit-btn"
                    onClick={() => navigate(`/iot-setting/${device.id}`)}
                  >
                    수정
                  </button>
                  <button
                    className="products-list-unsub-btn"
                    onClick={() => handleUnsubscribe(device.id)}
                  >
                    구독 취소
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="products-subscribe-section">
        <h2 className="products-subscribe-title">IOT 구독</h2>
        <button className="products-subscribe-btn" onClick={handleSubscribe}>구독하기</button>
      </div>
    </div>
  );
}

export default Products;