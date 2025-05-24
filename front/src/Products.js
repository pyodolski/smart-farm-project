import React, { useEffect, useState } from 'react';
import './Products.css';

function Products() {
  const [devices, setDevices] = useState([]);
  const [showSetting, setShowSetting] = useState(false);
  const [editTarget, setEditTarget] = useState(null);

  const loadDevices = () => {
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
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleSubscribe = () => {
    setEditTarget(null); // 새 구독
    setShowSetting(true);
  };

  const handleUnsubscribe = async (id) => {
    const confirmed = window.confirm("정말 구독을 취소하시겠습니까?");
    if (!confirmed) return;

    try {
      const res = await fetch(`http://localhost:5001/product/unsubscribe/${id}`, {
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
    <div className="products-container">
      <table className="products-table">
        <tbody>
          <tr>
            <td valign="top" width="300">
              <h3 className="products-title">내 IOT 구독</h3>
              {devices.length === 0 ? (
                <p>아직 구독한 기기가 없습니다.</p>
              ) : (
                <ul className="products-list">
                  {devices.map((device) => (
                    <li key={device.id} style={{ marginBottom: '10px' }}>
                      <strong>📷 {device.iot_name}</strong>
                      <div style={{ marginTop: '5px' }}>
                        <button
                          style={{ marginRight: '8px', padding: '4px 8px' }}
                          onClick={() => {
                            setEditTarget(device);
                            setShowSetting(true);
                          }}
                        >
                          수정
                        </button>
                        <button
                          style={{
                            padding: '4px 8px',
                            backgroundColor: '#ff5c5c',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px'
                          }}
                          onClick={() => handleUnsubscribe(device.id)}
                        >
                          구독 취소
                        </button>
                      </div>
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

      {showSetting && (
        <div className="modal">
          <CameraSetting
            initialData={editTarget}
            onComplete={(config) => {
              setShowSetting(false);
              setEditTarget(null);
              if (editTarget) {
                // 수정
                fetch(`http://localhost:5001/product/update/${editTarget.id}`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  credentials: "include",
                  body: JSON.stringify(config)
                })
                  .then(res => res.json())
                  .then(data => {
                    alert("✅ " + data.message);
                    loadDevices();
                  })
                  .catch(err => {
                    alert("❌ 수정 실패");
                    console.error(err);
                  });
              } else {
                // 새 구독
                fetch("http://localhost:5001/product/subscribe", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  credentials: "include",
                  body: JSON.stringify(config)
                })
                  .then(res => res.json())
                  .then(data => {
                    alert("✅ " + data.message);
                    loadDevices();
                  })
                  .catch(err => {
                    alert("❌ 등록 실패");
                    console.error(err);
                  });
              }
            }}
            onCancel={() => {
              setShowSetting(false);
              setEditTarget(null);
            }}
          />
        </div>
      )}
    </div>
  );
}

function CameraSetting({ onComplete, onCancel, initialData }) {
  const [iotName, setIotName] = useState(initialData?.iot_name || '');
  const [ghId, setGhId] = useState(initialData?.gh_id || '');
  const [greenhouseList, setGreenhouseList] = useState([]);
  const [interval, setInterval] = useState(parseInt(initialData?.capture_interval) || 15);
  const [direction, setDirection] = useState(initialData?.direction || 'both');
  const [resolution, setResolution] = useState(initialData?.resolution || '1280x720');
  const [enabled, setEnabled] = useState(initialData?.camera_on ?? true);

  useEffect(() => {
    fetch("http://localhost:5001/product/my_greenhouses", {
      credentials: "include"
    })
      .then(res => res.json())
      .then(data => {
        if (data.greenhouses) {
          setGreenhouseList(data.greenhouses);
        }
      })
      .catch(err => console.error("비닐하우스 목록 불러오기 실패:", err));
  }, []);

  const handleFinish = () => {
    if (!iotName || !ghId) {
      alert("기기 이름과 비닐하우스를 선택해주세요!");
      return;
    }

    const config = {
      iot_name: iotName,
      gh_id: parseInt(ghId),
      capture_interval: String(interval),
      direction,
      resolution,
      camera_on: enabled
    };
    onComplete(config);
  };

  const buttonStyle = (active) => ({
    backgroundColor: active ? '#81d27a' : '#eee',
    marginRight: '8px',
    padding: '5px 10px',
    fontSize: '0.8rem',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer'
  });

  return (
    <div style={{
      padding: "20px",
      backgroundColor: "#fff",
      border: "1px solid #ccc",
      borderRadius: "10px",
      width: "300px"
    }}>
      <h2>📷 카메라 설정</h2>

      <div style={{ marginBottom: "10px" }}>
        <label>
          <strong>기기 이름:</strong><br />
          <input
            type="text"
            value={iotName}
            onChange={(e) => setIotName(e.target.value)}
            placeholder="예: 딸기하우스1번"
            style={{ width: '100%', padding: '5px', marginTop: '5px' }}
          />
        </label>
      </div>

      <div style={{ marginBottom: "10px" }}>
        <label>
          <strong>비닐하우스 선택:</strong><br />
          <select
            value={ghId}
            onChange={(e) => setGhId(e.target.value)}
            // ✅ disabled 제거!
            style={{ width: '100%', padding: '5px', marginTop: '5px' }}
          >
            <option value="">-- 선택해주세요 --</option>
            {greenhouseList.map((gh) => (
              <option key={gh.id} value={gh.id}>
                {gh.greenhouse_name} (ID: {gh.id})
              </option>
            ))}
          </select>
        </label>
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>촬영 주기:</strong><br />
        {[5, 15, 30].map((sec) => (
          <button key={sec} onClick={() => setInterval(sec)} style={buttonStyle(interval === sec)}>
            {sec}초
          </button>
        ))}
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>방향:</strong><br />
        {["left", "right", "both"].map((dir) => (
          <button key={dir} onClick={() => setDirection(dir)} style={buttonStyle(direction === dir)}>
            {dir === "left" ? "좌" : dir === "right" ? "우" : "좌우"}
          </button>
        ))}
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>해상도:</strong><br />
        {["640x480", "1280x720", "1920x1080"].map((res) => (
          <button key={res} onClick={() => setResolution(res)} style={buttonStyle(resolution === res)}>
            {res}
          </button>
        ))}
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>카메라 상태:</strong><br />
        <button onClick={() => setEnabled(true)} style={buttonStyle(enabled)}>ON</button>
        <button onClick={() => setEnabled(false)} style={buttonStyle(!enabled)}>OFF</button>
      </div>

      <div style={{ marginTop: "15px" }}>
        <button onClick={handleFinish} style={{
          backgroundColor: '#59c02a', color: 'white', padding: '6px 12px', borderRadius: '6px', border: 'none', marginRight: '10px'
        }}>설정 완료</button>
        <button onClick={onCancel} style={{
          backgroundColor: '#ccc', color: '#333', padding: '6px 12px', borderRadius: '6px', border: 'none'
        }}>취소</button>
      </div>
    </div>
  );
}

export default Products;
