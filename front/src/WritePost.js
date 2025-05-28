import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './WritePost.css';
import API_BASE_URL from './config';

function WritePost() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('${API_BASE_URL}/api/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          title,
          content
        })
      });

      if (response.ok) {
        navigate('/community');
      } else {
        const data = await response.json();
        alert(data.message || '게시글 작성에 실패했습니다.');
      }
    } catch (error) {
      console.error('게시글 작성 실패:', error);
      alert('게시글 작성에 실패했습니다.');
    }
  };

  return (
    <div className="write-post-container">
      <h2>새 게시글 작성</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">제목</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="제목을 입력하세요"
          />
        </div>

        <div className="form-group">
          <label htmlFor="content">내용</label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            required
            placeholder="내용을 입력하세요"
          />
        </div>

        <div className="button-group">
          <button type="submit">작성하기</button>
          <button 
            type="button" 
            onClick={() => navigate('/community')}
            className="cancel-button"
          >
          취소
          </button>
        </div>
      </form>
    </div>
  );
}

export default WritePost; 