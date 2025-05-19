import React, { useEffect, useState } from 'react';

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
    <div>
      <table>
        <tr>
          <td valign="top" width="250">
            <h3>내 IOT 구독</h3>
            {devices.length === 0 ? (
              <p>아직 구독한 기기가 없습니다.</p>
            ) : (
              <ul>
                {devices.map((device, index) => (
                  <li key={device.id}>
                    {index + 1}. 시작일: {new Date(device.start_date).toLocaleString()}
                  </li>
                ))}
              </ul>
            )}
          </td>

          <td valign="top" style={{ paddingLeft: "40px" }}>
            <h2>IOT 구독</h2>
            <button onClick={handleSubscribe}>구독하기</button>
          </td>
        </tr>
      </table>
    </div>
  );
}

export default Products;
