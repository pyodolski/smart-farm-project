import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API_BASE_URL from '../../utils/config';
import './FarmDetail.css';
import { GoSidebarCollapse, GoSidebarExpand } from "react-icons/go";
import { FaCamera, FaEdit, FaTrash } from "react-icons/fa";
import { GrLinkPrevious, GrFormPrevious } from "react-icons/gr";
import { AnimatePresence, motion } from "framer-motion";

function FarmDetail() {
  const { farmId } = useParams();
  const [farm, setFarm] = useState(null);
  const [greenhouses, setGreenhouses] = useState([]);
  const [selectedGh, setSelectedGh] = useState(null);
  const [gridData, setGridData] = useState(null);
  const [numRows, setNumRows] = useState(0);
  const [numCols, setNumCols] = useState(0);
  const [weather, setWeather] = useState(null);
  const [twoDay, setTwoDay] = useState([]);
  const [sensor, setSensor] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [error, setError] = useState('');
  const [groups, setGroups] = useState(null);
  const [groupAxis, setGroupAxis] = useState(null);
  const [showIotModal, setShowIotModal] = useState(false);
  const [iotList, setIotList] = useState([]);
  const [selectedIot, setSelectedIot] = useState(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editGrid, setEditGrid] = useState(null);
  const [grid, setGrid] = useState(Array(10).fill(Array(10).fill(0)));
  const [selectedBar, setSelectedBar] = useState(null);
  const [barDetailDirection, setBarDetailDirection] = useState('in');
  const [barDetailIndex, setBarDetailIndex] = useState(null);

  // 그리드 타입 매핑
  const gridTypeMapping = {
    0: { label: '길', color: '#F9F7E8' },
    1: { label: '딸기', color: '#FF8B8B' },
    2: { label: '토마토', color: '#61BFAD' }
  };

  const navigate = useNavigate();

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/farms/${farmId}`, {
      credentials: 'include'
    })
      .then(res => {
        if (!res.ok) throw new Error('농장 정보를 불러오는데 실패했습니다.');
        return res.json();
      })
      .then(data => setFarm(data))
      .catch(err => setError(err.message));
  }, [farmId]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/greenhouses/list/${farmId}`, {
      credentials: 'include'
    })
      .then((res) => {
        if (!res.ok) throw new Error('온실 목록을 불러오는데 실패했습니다.');
        return res.json();
      })
      .then((data) => {
        const greenhousesData = data && data.greenhouses ? data.greenhouses : [];
        setGreenhouses(greenhousesData);
        if (greenhousesData.length > 0) setSelectedGh(greenhousesData[0]);
      })
      .catch(err => {
        setError(err.message);
        setGreenhouses([]);
      });
  }, [farmId]);

  useEffect(() => {
    if (!farm || !farm.location) return;
    fetch(`${API_BASE_URL}/api/weather?city=${encodeURIComponent(farm.location)}`, {
      credentials: 'include'
    })
      .then(res => {
        if (!res.ok) throw new Error('날씨 정보를 불러오는데 실패했습니다.');
        return res.json();
      })
      .then(data => {
        setWeather(data.weather);
        setTwoDay(data.two_day || []);
      })
      .catch(err => setError(err.message));
  }, [farm]);

  useEffect(() => {
    if (!selectedGh) return;
    fetch(`${API_BASE_URL}/api/greenhouses/api/grid?id=${selectedGh.id}`, {
      credentials: 'include'
    })
      .then(res => {
        if (!res.ok) throw new Error('그리드 데이터를 불러오는데 실패했습니다.');
        return res.json();
      })
      .then(data => {
        let grid = data.grid_data;
        if (typeof grid === 'string') {
          try { grid = JSON.parse(grid); } catch {}
        }
        setGridData(grid);
        setNumRows(data.num_rows);
        setNumCols(data.num_cols);
      })
      .catch(err => setError(err.message));

    fetch(`${API_BASE_URL}/api/greenhouses/${selectedGh.id}/groups`, {
      credentials: 'include'
    })
      .then(res => {
        if (!res.ok) throw new Error('그룹 정보를 불러오는데 실패했습니다.');
        return res.json();
      })
      .then(data => {
        setGroups(data.groups);
        setGroupAxis(data.axis);
      })
      .catch(err => setError(err.message));
  }, [selectedGh]);

  const handleSidebarToggle = () => setSidebarOpen((open) => !open);
  const handleAddGreenhouse = () => navigate(`/greenhouse-grid/${farmId}`);

  const handleCapture = async () => {
    try {
      const response = await fetch('/product/api/iot/list', {
        credentials: 'include'
      });
      const data = await response.json();
      if (!data.iot_list || data.iot_list.length === 0) {
        alert('IoT를 구독해주세요.');
        return;
      }
      setIotList(data.iot_list);
      setShowIotModal(true);
    } catch (err) {
      setError('IoT 목록을 불러오는데 실패했습니다.');
    }
  };

  const handleEdit = () => {
    if (!selectedGh) return;
    console.log('수정할 grid_data:', gridData);
    navigate(`/greenhouse-grid/${farmId}?edit=${selectedGh.id}`, {
      state: {
        greenhouseId: selectedGh.id,
        gridData,
        numRows,
        numCols,
        houseName: selectedGh.name
      }
    });
  };

  const handleGridCellChange = (row, col, value) => {
    const newGrid = editGrid.map(arr => arr.slice());
    newGrid[row][col] = value;
    setEditGrid(newGrid);
  };

  const handleSaveGrid = async () => {
    if (!selectedGh) return;
    try {
      await fetch(`${API_BASE_URL}/api/greenhouses/update/${selectedGh.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: selectedGh.name,
          num_rows: numRows,
          num_cols: numCols,
          grid_data: editGrid
        })
      });
      setIsEditMode(false);
      setGridData(editGrid);
    } catch (err) {
      setError('그리드 저장에 실패했습니다.');
    }
  };

  const handleCancelEdit = () => {
    setIsEditMode(false);
    setEditGrid(null);
  };

  const handleDelete = async () => {
    if (!selectedGh || !window.confirm('정말로 이 하우스를 삭제하시겠습니까?')) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/greenhouses/${selectedGh.id}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      if (!response.ok) throw new Error('하우스 삭제에 실패했습니다.');
      const updatedGreenhouses = greenhouses.filter(gh => gh.id !== selectedGh.id);
      setGreenhouses(updatedGreenhouses);
      if (updatedGreenhouses.length > 0) {
        setSelectedGh(updatedGreenhouses[0]);
      } else {
        setSelectedGh(null);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleIotSelect = (iot) => {
    setSelectedIot(iot);
  };

  const handleIotConfirm = async () => {
    /*
    여기에 촬영할 iot 데이터 전송 코드 추가
    */
  };

  function weatherIcon(description) {
    if (!description) return '🌤️';
    const desc = description.toLowerCase();
    if (desc.includes('비')) return '🌧️';
    if (desc.includes('눈')) return '❄️';
    if (desc.includes('구름')) return '☁️';
    if (desc.includes('맑')) return '☀️';
    if (desc.includes('흐림')) return '🌥️';
    if (desc.includes('번개')) return '⛈️';
    if (desc.includes('안개')) return '🌫️';
  }

  const renderGrid = () => {
    return (
      <div className="grid-container">
        {grid.map((row, i) => (
          <div key={i} className="grid-row">
            {row.map((cell, j) => (
              <div
                key={`${i}-${j}`}
                className={`grid-cell type-${cell}`}
                onClick={() => handleCellClick(i, j)}
              >
                {gridTypeMapping[cell].label}
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const handleCellClick = (row, col) => {
    const newGrid = grid.map(r => [...r]);
    newGrid[row][col] = (newGrid[row][col] + 1) % 3; // 0, 1, 2 순환
    setGrid(newGrid);
  };

  const renderMergedBars = () => {
    if (!groups || !groupAxis) return null;
    return (
      <div className="merged-bar-container">
        {groupAxis === 'row' && (
          <div className="merged-bar-container">
            {groups.map((group, idx) => {
              const [rowIdx, startCol, endCol, value] = group;
              return (
                <div
                  key={`row-${idx}`}
                  className={`merged-bar type-${value}`}
                  style={{
                    width: `${(endCol - startCol + 1) * 45}px`,
                    height: '45px',
                    marginBottom: '6px',
                    marginLeft: `${startCol * 45}px`,
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setBarDetailDirection(1);
                    setSelectedBar({ group, axis: groupAxis });
                  }}
                >
                  {gridTypeMapping[value].label}
                </div>
              );
            })}
          </div>
        )}
        {groupAxis === 'col' && (
          <div className="merged-bar-col-wrapper">
            {groups.map((group, idx) => {
              const [startRow, colIdx, endRow, value] = group;
              return (
                <div
                  key={`col-${idx}`}
                  className={`merged-bar type-${value}`}
                  style={{
                    width: '45px',
                    height: `${(endRow - startRow + 1) * 45}px`,
                    marginRight: '6px',
                    marginTop: `${startRow * 45}px`,
                    writingMode: 'vertical-rl',
                    textAlign: 'center',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer'
                  }}
                  onClick={() => {
                    setBarDetailDirection(1);
                    setSelectedBar({ group, axis: groupAxis });
                  }}
                >
                  {gridTypeMapping[value].label}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  const weatherStepsIn = [
    { style: { opacity: 0, transform: 'translateX(-80px)' }, duration: 400 },
    { style: { opacity: 1, transform: 'translateX(0)' }, duration: 400 }
  ];
  const weatherStepsOut = [
    { style: { opacity: 1, transform: 'translateX(0)' }, duration: 400 },
    { style: { opacity: 0, transform: 'translateX(-80px)' }, duration: 400 }
  ];
  const barDetailStepsIn = [
    { style: { opacity: 0, transform: 'translateX(80px)' }, duration: 400 },
    { style: { opacity: 1, transform: 'translateX(0)' }, duration: 400 }
  ];
  const barDetailStepsOut = [
    { style: { opacity: 1, transform: 'translateX(0)' }, duration: 400 },
    { style: { opacity: 0, transform: 'translateX(80px)' }, duration: 400 }
  ];

  return (
    <div className="farmdetail-container">
      <aside className={`farmdetail-sidebar${sidebarOpen ? '' : ' closed'}`}>
        <div className="farmdetail-sidebar-header">
          <h3 className={`farmdetail-sidebar-title${sidebarOpen ? '' : ' hidden'}`}>비닐하우스 목록</h3>
          <button
            className="farmdetail-sidebar-toggle"
            onClick={handleSidebarToggle}
            aria-label={sidebarOpen ? '사이드바 접기' : '사이드바 펴기'}
            style={{ background: 'none', border: 'none', boxShadow: 'none', padding: 0, cursor: 'pointer' }}
          >
            {sidebarOpen ? <GoSidebarExpand size={26} /> : <GoSidebarCollapse size={26} />}
          </button>
        </div>
        {sidebarOpen && (
          <>
            {greenhouses.length === 0 ? (
            <p className="farmdetail-empty">등록된 비닐하우스가 없습니다.</p>
          ) : (
              <>
            <ul className="farmdetail-list">
              {greenhouses.map((gh) => (
                    <li
                      key={gh.id}
                      onClick={() => {
                        setSelectedGh(gh);
                        setSelectedBar(null);
                        setBarDetailDirection('in');
                      }}
                      style={{ background: selectedGh && selectedGh.id === gh.id ? '#e6f2d6' : undefined }}
                    >
                      {gh.name}
                    </li>
              ))}
            </ul>
                <button className="farmdetail-add-btn" onClick={handleAddGreenhouse}>
                  + 비닐하우스 추가
                </button>
              </>
            )}
          </>
        )}
      </aside>
      <main className="farmdetail-main">
        {greenhouses.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <button className="farmdetail-empty-btn" onClick={handleAddGreenhouse}>
              + 비닐하우스 추가
            </button>
          </div>
        ) : (
          <>
            <div className="farm-info-card-col">
              {farm && (
                <div className="farm-info-card">
                  <div className="farm-info-header">
                    <h2>{farm.name}농장</h2>
                    <div className="location">위치: {farm.location}</div>
                  </div>
                  <div className="farm-info-content">
                    <h3 className="grid-title">{selectedGh?.name} 하우스</h3>
                    {isEditMode ? (
                      <div className="grid-container">
                        {editGrid && editGrid.map((row, rowIdx) => (
                          <div key={rowIdx} style={{ display: 'flex' }}>
                            {row.map((cell, colIdx) => (
                              <input
                                key={colIdx}
                                type="number"
                                value={cell}
                                min={0}
                                max={2}
                                style={{ width: 40, height: 40, textAlign: 'center', margin: 2, borderRadius: 6, border: '1px solid #ccc' }}
                                onChange={e => handleGridCellChange(rowIdx, colIdx, Number(e.target.value))}
                              />
                            ))}
                          </div>
                        ))}
                        <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
                          <button className="control-btn edit" onClick={handleSaveGrid}>저장</button>
                          <button className="control-btn delete" onClick={handleCancelEdit}>취소</button>
                        </div>
                      </div>
                    ) : (
                      (groups && groupAxis) && (
                        <div className="merged-bar-container">
                          {groupAxis === 'row' && (
                            <div className="merged-bar-container">
                              {groups.map((group, idx) => {
                                const [rowIdx, startCol, endCol, value] = group;
                                return (
                                  <div
                                    key={`row-${idx}`}
                                    className={`merged-bar type-${value}`}
                                    style={{
                                      width: `${(endCol - startCol + 1) * 45}px`,
                                      height: '45px',
                                      marginBottom: '6px',
                                      marginLeft: `${startCol * 45}px`,
                                      cursor: 'pointer'
                                    }}
                                    onClick={() => {
                                      setBarDetailDirection(1);
                                      setSelectedBar({ group, axis: groupAxis });
                                    }}
                                  >
                                    {gridTypeMapping[value].label}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                          {groupAxis === 'col' && (
                            <div className="merged-bar-col-wrapper">
                              {groups.map((group, idx) => {
                                const [startRow, colIdx, endRow, value] = group;
                                return (
                                  <div
                                    key={`col-${idx}`}
                                    className={`merged-bar type-${value}`}
                                    style={{
                                      width: '45px',
                                      height: `${(endRow - startRow + 1) * 45}px`,
                                      marginRight: '6px',
                                      marginTop: `${startRow * 45}px`,
                                      writingMode: 'vertical-rl',
                                      textAlign: 'center',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      cursor: 'pointer'
                                    }}
                                    onClick={() => {
                                      setBarDetailDirection(1);
                                      setSelectedBar({ group, axis: groupAxis });
                                    }}
                                  >
                                    {gridTypeMapping[value].label}
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </div>
            <div className="weather-card-col">
              <AnimatePresence initial={false} custom={barDetailDirection}>
                {(!selectedBar && weather) ? (
                  <motion.div
                    key="weather"
                    initial={{ opacity: 0, x: barDetailDirection === -1 ? 80 : -80 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: barDetailDirection === -1 ? -80 : 80 }}
                    transition={{ type: "spring", bounce: 0.3, duration: 0.8 }}
                    className="weather-card"
                    style={{ position: "absolute", width: "100%" }}
                  >
                    <div className="weather-header">
                      <h3 className="weather-title">오늘의 날씨</h3>
                      <select className="city-select" value={farm?.location || ''} disabled>
                        <option>{farm?.location || ''}</option>
                      </select>
                    </div>
                    <div className="weather-today">
                      <div className="weather-icon">{weatherIcon(weather.description)}</div>
                      <div className="weather-info">
                        <div className="weather-temp">{weather.temperature}°C</div>
                        <div className="weather-desc">{weather.description}</div>
                      </div>
                    </div>
                    <div className="weather-forecast-title">내일/모레 예보</div>
                    <div className="weather-forecast-row">
                      {twoDay && twoDay.length > 0 && twoDay.some(day => day.min_temp !== '-') ? (
                        twoDay.map(day => (
                          <div className="forecast-card" key={day.date}>
                            <div className="forecast-date">{day.date}</div>
                            <div className="forecast-temp">
                              {day.min_temp !== '-' ? `${day.min_temp}°C ~ ${day.max_temp}°C` : '예보 없음'}
                            </div>
                            <div className="forecast-desc">{day.description} {weatherIcon(day.description)}</div>
                          </div>
                        ))
                      ) : (
                        <>
                          <div className="forecast-card">내일 예보 없음</div>
                          <div className="forecast-card">모레 예보 없음</div>
                        </>
                      )}
                    </div>
                    <hr className="weather-divider" />
                    <div className="env-card">
                      <div className="env-title">하우스 환경</div>
                      <div className="env-info-row">
                        <span className="env-label">온도</span>
                        <span className="env-value">25.5°C</span>
                      </div>
                      <div className="env-info-row">
                        <span className="env-label">습도</span>
                        <span className="env-value">64%</span>
                      </div>
                      <div className="env-info-row">
                        <span className="env-label">측정 시간</span>
                        <span className="env-value">2024-06-12 15:30:00</span>
                      </div>
                    </div>
                  </motion.div>
                ) : null}
                {selectedBar && selectedBar.group ? (
                  <motion.div
                    key="bar-detail"
                    initial={false}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: barDetailDirection === -1 ? 80 : -80 }}
                    transition={{ type: "spring", bounce: 0.3, duration: 0.8 }}
                    className="bar-detail-card"
                    style={{ position: "absolute", width: "100%" }}
                  >
                    <div className="bar-detail-back" onClick={() => {
                      setBarDetailDirection(-1);
                      setSelectedBar(null);
                    }}>
                      <GrFormPrevious size={30} />
                    </div>
                    <div className="bar-detail-content">
                      {selectedBar.axis === 'row' ? (
                        <h2>{selectedBar.group[0] + 1}행 상세 정보</h2>
                      ) : (
                        <h2>{selectedBar.group[1] + 1}열 상세 정보</h2>
                      )}
                      <div>타입: <b
                        className={selectedBar.group[3] === 0 ? "bar-label-outline" : ""}
                        style={{ color: gridTypeMapping[selectedBar.group[3]].color }}
                      >
                        {gridTypeMapping[selectedBar.group[3]].label}
                      </b></div>
                      {selectedBar.axis === 'row' ? (
                        <>
                          <div>행: {selectedBar.group[0] + 1}행</div>
                          <div>길이: {selectedBar.group[2] - selectedBar.group[1] + 1}m</div>
                        </>
                      ) : (
                        <>
                          <div>열: {selectedBar.group[1] + 1}열</div>
                          <div>길이: {selectedBar.group[2] - selectedBar.group[0] + 1}m</div>
                        </>
                      )}
                    </div>
                  </motion.div>
                ) : null}
              </AnimatePresence>
            </div>
            <div className="control-card-col">
              {selectedGh && (
                <div className="control-card">
                  <button className="control-btn capture" onClick={handleCapture}>
                    <FaCamera /> 촬영
                  </button>
                  <button className="control-btn edit" onClick={handleEdit}>
                    <FaEdit /> 수정
                  </button>
                  <button className="control-btn delete" onClick={handleDelete}>
                    <FaTrash /> 삭제
                  </button>
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {showIotModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">IoT 할당</h2>
            </div>
            <div className="iot-list">
              {iotList.map(iot => (
                <div
                  key={iot.id}
                  className={`iot-item ${selectedIot?.id === iot.id ? 'selected' : ''}`}
                  onClick={() => handleIotSelect(iot)}
                >
                  <div>
                    <div className="iot-item-name">{iot.name}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="modal-footer">
              <button className="modal-btn cancel" onClick={() => setShowIotModal(false)}>
                취소
              </button>
              <button
                className="modal-btn confirm"
                onClick={handleIotConfirm}
                disabled={!selectedIot}
              >
                확인
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FarmDetail;
