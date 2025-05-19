import React, { useState } from 'react';

function CameraSetting() {
  const [interval, setInterval] = useState(60);
  const [direction, setDirection] = useState('both');
  const [resolution, setResolution] = useState('640x480');
  const [enabled, setEnabled] = useState(true);
  const [message, setMessage] = useState('');

  const sendConfig = async () => {
    const config = { interval, direction, resolution, enabled };
    try {
      const res = await fetch("http://localhost:5001/api/iot/camera-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(config)
      });
      const data = await res.json();
      setMessage(data.message || "설정 전송 완료");
    } catch (err) {
      console.error(err);
      setMessage("설정 전송 실패");
    }
  };

  // 공통 버튼 스타일
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
    <div style={{ padding: "20px" }}>
      <h2>📷 카메라 설정</h2>

      <div style={{ marginBottom: "10px" }}>
        <strong>촬영 주기:</strong><br />
        <div style={{ display: 'flex', flexDirection: 'row', marginTop: '5px' }}>
          {[5, 15, 30].map(sec => (
            <button
              key={sec}
              onClick={() => setInterval(sec)}
              style={buttonStyle(interval === sec)}
            >
              {sec === 5 ? "5초" : sec === 15 ? "15초" : "30초"}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>촬영 방향:</strong><br />
        <div style={{ display: 'flex', flexDirection: 'row', marginTop: '5px' }}>
          {["left", "right", "both"].map(dir => (
            <button
              key={dir}
              onClick={() => setDirection(dir)}
              style={buttonStyle(direction === dir)}
            >
              {dir === "left" ? "좌측" : dir === "right" ? "우측" : "좌/우 모두"}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>해상도:</strong><br />
        <div style={{ display: 'flex', flexDirection: 'row', marginTop: '5px' }}>
          {["640x480", "1280x720", "1920x1080"].map(res => (
            <button
              key={res}
              onClick={() => setResolution(res)}
              style={buttonStyle(resolution === res)}
            >
              {res}
            </button>
          ))}
        </div>
      </div>

      <div style={{ marginBottom: "10px" }}>
        <strong>카메라 작동:</strong><br />
        <div style={{ display: 'flex', flexDirection: 'row', marginTop: '5px' }}>
          <button
            onClick={() => setEnabled(true)}
            style={buttonStyle(enabled)}
          >
            ON
          </button>
          <button
            onClick={() => setEnabled(false)}
            style={buttonStyle(!enabled)}
          >
            OFF
          </button>
        </div>
      </div>

      <button
        onClick={sendConfig}
        style={{
          marginTop: '20px',
          padding: '8px 16px',
          backgroundColor: '#59c02a',
          color: 'white',
          fontWeight: 'bold',
          fontSize: '0.85rem',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}
      >
        설정 전송
      </button>

      {message && <p style={{ marginTop: '10px', color: 'green' }}>{message}</p>}
    </div>
  );
}

export default CameraSetting;
