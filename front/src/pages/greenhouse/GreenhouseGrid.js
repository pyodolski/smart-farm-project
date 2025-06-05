import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import API_BASE_URL from '../../utils/config';
import './GreenhouseGrid.css';

function GreenhouseGrid() {
  const navigate = useNavigate();
  const { farmId, greenhouseId } = useParams();
  const location = useLocation();
  // location.state로 farmId, greenhouseId, houseName, numRows, numCols, gridData 등을 받을 수 있음

  // 초기값 세팅
  const [houseName, setHouseName] = useState(location.state?.houseName || '');
  const [rows, setRows] = useState(location.state?.numRows || 10);
  const [cols, setCols] = useState(location.state?.numCols || 10);
  const [gridData, setGridData] = useState(location.state?.gridData || Array.from({length: rows}, () => Array(cols).fill(0)));
  const [currentValue, setCurrentValue] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    // 행/열 변경 시 그리드 크기 조정
    setGridData(prev => {
      const newGrid = [];
      for (let r = 0; r < rows; r++) {
        const row = [];
        for (let c = 0; c < cols; c++) {
          row.push((prev[r] && prev[r][c] !== undefined) ? prev[r][c] : 0);
        }
        newGrid.push(row);
      }
      return newGrid;
    });
  }, [rows, cols]);

  const getColor = (value) => {
    if (value === 0) return 'red';
    if (value === 1) return 'black';
    if (value === 2) return 'blue';
    return 'lightgray';
  };

  const handleCellClick = (r, c) => {
    setGridData(prev => {
      const copy = prev.map(row => [...row]);
      copy[r][c] = currentValue;
      return copy;
    });
  };

  const handleCellMouseDown = (r, c) => {
    setIsDragging(true);
    handleCellClick(r, c);
  };

  const handleCellMouseEnter = (r, c) => {
    if (isDragging) handleCellClick(r, c);
  };

  useEffect(() => {
    const handleMouseUp = () => setIsDragging(false);
    document.addEventListener('mouseup', handleMouseUp);
    return () => document.removeEventListener('mouseup', handleMouseUp);
  }, []);

  const handleSubmit = async () => {
    const payload = {
      farm_id: parseInt(farmId),
      name: houseName,
      num_rows: rows,
      num_cols: cols,
      grid_data: gridData
    };
    console.log(payload);
    const endpoint = greenhouseId ? `/api/greenhouses/update/${greenhouseId}` : '/api/greenhouses/create';
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      alert(data.message);
      if (response.ok) navigate(-1); // 저장 후 뒤로가기
    } catch (err) {
      alert('저장 중 오류 발생');
    }
  };

  return (
    <div className="greenhouse-container">
      <div className="greenhouse-header">
        <button className="farm-back-button" onClick={() => navigate(-1)}>⬅ 뒤로가기</button>
        <h2 className="greenhouse-title">🧱 비닐하우스 그리드 생성기</h2>
      </div>
      
      <div className="controls-container">
        <div className="control-group">
          <label>하우스 이름:</label>
          <input 
            type="text" 
            className="text-input"
            value={houseName} 
            onChange={e => setHouseName(e.target.value)} 
            placeholder="예: 1동"
          />
        </div>
        <div className="control-group">
          <label>행:</label>
          <input 
            type="number" 
            className="control-input"
            value={rows} 
            min={1} 
            onChange={e => setRows(Number(e.target.value))} 
          />
        </div>
        <div className="control-group">
          <label>열:</label>
          <input 
            type="number" 
            className="control-input"
            value={cols} 
            min={1} 
            onChange={e => setCols(Number(e.target.value))} 
          />
        </div>
        <div className="control-group right-controls">
          <div className="value-selector">
            <label>선택 값:</label>
            {[
              { value: 0, color: 'red' },
              { value: 1, color: 'black' },
              { value: 2, color: 'blue' }
            ].map(({ value, color }) => (
              <button
                key={value}
                className={`value-button ${currentValue === value ? 'active' : ''} ${color}`}
                onClick={() => setCurrentValue(value)}
              >
                {value}
              </button>
            ))}
          </div>
          <button 
            className="control-button"
            onClick={handleSubmit}
          >
            ✅ 저장
          </button>
        </div>
      </div>

      <div
        className="grid-container"
        style={{
          gridTemplateColumns: `repeat(${cols}, 35px)`,
          gridTemplateRows: `repeat(${rows}, 35px)`,
        }}
      >
        {gridData.map((row, r) =>
          row.map((value, c) => (
            <div
              key={`${r}-${c}`}
              className={`grid-cell ${getColor(value)}`}
              onMouseDown={() => handleCellMouseDown(r, c)}
              onMouseEnter={() => handleCellMouseEnter(r, c)}
              onClick={() => handleCellClick(r, c)}
            >
              {value}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default GreenhouseGrid; 