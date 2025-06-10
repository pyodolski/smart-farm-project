import { useState, useCallback } from 'react';

export const useGrid = (initialRows = 10, initialCols = 10, initialData = null) => {
  const [dimensions, setDimensions] = useState({
    rows: initialRows,
    cols: initialCols
  });

  const [grid, setGrid] = useState(() => {
    if (initialData) return initialData;
    return Array(initialRows).fill().map(() => Array(initialCols).fill(0));
  });

  const updateDimensions = useCallback((newRows, newCols) => {
    setDimensions({ rows: newRows, cols: newCols });
    setGrid(prev => {
      const newGrid = Array(newRows).fill().map(() => Array(newCols).fill(0));
      // 기존 데이터 복사
      for (let i = 0; i < Math.min(prev.length, newRows); i++) {
        for (let j = 0; j < Math.min(prev[i].length, newCols); j++) {
          newGrid[i][j] = prev[i][j];
        }
      }
      return newGrid;
    });
  }, []);

  const updateCell = useCallback((row, col, value) => {
    setGrid(prev => {
      const newGrid = prev.map(arr => [...arr]);
      newGrid[row][col] = value;
      return newGrid;
    });
  }, []);

  const resetGrid = useCallback(() => {
    setGrid(Array(dimensions.rows).fill().map(() => Array(dimensions.cols).fill(0)));
  }, [dimensions]);

  return {
    dimensions,
    grid,
    setGrid,
    updateDimensions,
    updateCell,
    resetGrid
  };
}; 