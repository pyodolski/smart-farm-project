import React, { useEffect, useState } from "react";
import "./SensorPage.css"; // 필요 시 스타일 분리

function SensorPage() {
  const [sensorData, setSensorData] = useState({
    temperature: "--",
    humidity: "--",
    timestamp: "--",
  });

  useEffect(() => {
    fetch("/product/last-sensor")
      .then((res) => res.json())
      .then((data) => {
        setSensorData({
          temperature: data.temperature,
          humidity: data.humidity,
          timestamp: new Date(data.timestamp).toLocaleString(),
        });
      })
      .catch((err) => {
        console.error("센서 데이터 불러오기 실패:", err);
      });
  }, []);

  return (
    <div className="sensor-container">
      <h1>📷 이미지 및 🌡️ 센서 데이터</h1>
      <img
        src="/static/images/last.jpg"
        alt="최근 이미지"
        className="sensor-image"
      />
      <div className="sensor-data">
        <p>🌡️ 온도: {sensorData.temperature}°C</p>
        <p>💧 습도: {sensorData.humidity}%</p>
        <p>⏱️ {sensorData.timestamp}</p>
      </div>
    </div>
  );
}

export default SensorPage;