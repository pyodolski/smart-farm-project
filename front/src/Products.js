import React, { useEffect, useState } from 'react';
import './Products.css';

function Products() {
  const [devices, setDevices] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5001/product/my_devices", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        if (data.devices) {
          setDevices(data.devices);
        }
      })
      .catch(err => console.error("구독 목록 불러오기 실패:", err));
  }, []);

  const handleSubscribe = async () => {
    const confirmed = window.confirm("IOT를 구독하시겠습니까?");
    if (!confirmed) return;

    try {
      const res = await fetch("http://localhost:5001/product/subscribe", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json"
        }
      });

      const data = await res.json();
      if (res.ok) {
        alert("✅ " + data.message);
        window.location.reload();
      } else {
        alert("❌ " + data.message);
      }
    } catch (err) {
      alert("❌ 서버 오류 발생");
      console.error(err);
    }
  };

  return (
    <div className="products-container">
      <table className="products-table">
        <tbody>
          <tr>
            <td valign="top" width="250">
              <h3 className="products-title">내 IOT 구독</h3>
              {devices.length === 0 ? (
                <p>아직 구독한 기기가 없습니다.</p>
              ) : (
                <ul className="products-list">
                  {devices.map((device, index) => (
                    <li key={device.id}>
                      {index + 1}. 시작일: {new Date(device.start_date).toLocaleString()}
                    </li>
                  ))}
                </ul>
              )}
            </td>
            <td valign="top" className="products-subscribe-section">
              <h2 className="products-subscribe-title">IOT 구독</h2>
              <button className="products-subscribe-btn" onClick={handleSubscribe}>구독하기</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default Products;
