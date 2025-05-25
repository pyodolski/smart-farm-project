import React from 'react';
import { useParams } from 'react-router-dom';

function FarmDetail() {
  const { farmId } = useParams();

  // 실제로는 farmId로 API 호출해서 상세 정보 받아와서 보여주면 됨
  return (
    <div>
      <h2>농장 상세 페이지</h2>
      <p>농장 ID: {farmId}</p>
      {/* 여기에 상세 정보 표시 */}
    </div>
  );
}

export default FarmDetail;
