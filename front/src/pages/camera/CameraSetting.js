import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './CameraSetting.css';
import API_BASE_URL from '../../utils/config';

function CameraSetting() {
  const [interval, setInterval] = useState(15);
  const [direction, setDirection] = useState('both');
  const [resolution, setResolution] = useState('640x480');
  const [enabled, setEnabled] = useState(true);
  const [message, setMessage] = useState('');
  const [iotName, setIotName] = useState('');
  const [device, setDevice] = useState(null);
  const navigate = useNavigate();
  const { deviceId } = useParams();

  useEffect(() => {
    // 수정 모드인 경우 기존 데이터 가져오기
    if (deviceId) {
      fetch(`${API_BASE_URL}/product/my_devices/${deviceId}`, {
        credentials: "include"
      })
        .then(res => {
          if (!res.ok) {
            throw new Error('기기 정보를 불러올 수 없습니다');
          }
          return res.json();
        })
        .then(data => {
          if (data.device) {
            setIotName(data.device.iot_name);
            setInterval(parseInt(data.device.capture_interval));
            setDirection(data.device.direction);
            setResolution(data.device.resolution);
            setEnabled(data.device.camera_on);
            setDevice(data.device);
          } else {
            throw new Error('기기 정보가 없습니다');
          }
        })
        .catch(err => {
          console.error("기기 정보 불러오기 실패:", err);
          setMessage(err.message);
          setTimeout(() => navigate('/products'), 1500);
        });
    }
  }, [deviceId]);

  const sendConfig = async () => {
    if (!iotName) {
      setMessage("기기 이름을 입력해주세요!");
      return;
    }

    const config = {
      iot_name: iotName,
      capture_interval: String(interval),
      direction,
      resolution,
      camera_on: enabled
    };

    try {
      const url = deviceId
        ? `${API_BASE_URL}/product/update/${deviceId}`
        : `${API_BASE_URL}/product/subscribe`;

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(config)
      });
      const data = await res.json();
      setMessage(data.message || "설정 전송 완료");
      setTimeout(() => navigate('/products'), 1500);
    } catch (err) {
      console.error(err);
      setMessage("설정 전송 실패");
    }
  };

  return (
    <div className="camera-setting-container">
      <div className="camera-setting-flex">
        <div className="farm-house-section">
          <h4>기기 설정</h4>
          <div className="select-row">
            <label htmlFor="iot-name"><strong>기기 이름:</strong></label>
            <input
              id="iot-name"
              type="text"
              value={iotName}
              onChange={(e) => setIotName(e.target.value)}
              placeholder="예: 딸기하우스1번"
              className="select-box"
            />
          </div>
        </div>

        <div className="camera-section">
          <h2>📷 카메라 설정</h2>
          <div className="setting-group">
            <strong>촬영 주기:</strong>
            <div className="button-row">
              {[5, 15, 30].map(sec => (
                <button
                  key={sec}
                  onClick={() => setInterval(sec)}
                  className={`setting-btn${interval === sec ? ' active' : ''}`}
                >
                  {sec === 5 ? "5초" : sec === 15 ? "15초" : "30초"}
                </button>
              ))}
            </div>
          </div>
          <div className="setting-group">
            <strong>촬영 방향:</strong>
            <div className="button-row">
              {["left", "right", "both"].map(dir => (
                <button
                  key={dir}
                  onClick={() => setDirection(dir)}
                  className={`setting-btn${direction === dir ? ' active' : ''}`}
                >
                  {dir === "left" ? "좌측" : dir === "right" ? "우측" : "좌/우 모두"}
                </button>
              ))}
            </div>
          </div>
          <div className="setting-group">
            <strong>해상도:</strong>
            <div className="button-row">
              {["640x480", "1280x720", "1920x1080"].map(res => (
                <button
                  key={res}
                  onClick={() => setResolution(res)}
                  className={`setting-btn${resolution === res ? ' active' : ''}`}
                >
                  {res}
                </button>
              ))}
            </div>
          </div>
          <div className="setting-group">
            <strong>카메라 작동:</strong>
            <div className="button-row">
              <button
                onClick={() => setEnabled(true)}
                className={`setting-btn${enabled ? ' active' : ''}`}
              >
                ON
              </button>
              <button
                onClick={() => setEnabled(false)}
                className={`setting-btn${!enabled ? ' active' : ''}`}
              >
                OFF
              </button>
            </div>
          </div>
          <button
            onClick={sendConfig}
            className="submit-btn"
          >
            설정 전송
          </button>
          {message && <p className="message-text">{message}</p>}
        </div>
      </div>
    </div>
  );
}

export default CameraSetting;