import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API_BASE_URL from './config';

function EditPost() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const { postId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPost();
  }, [postId]);

  const fetchPost = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setTitle(data.post.title);
        setContent(data.post.content);
      } else {
        navigate('/community');
      }
    } catch (error) {
      console.error('게시글 로딩 실패:', error);
      navigate('/community');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
        method: 'PUT',
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
        navigate(`/community/post/${postId}`);
      } else {
        const data = await response.json();
        alert(data.message || '게시글 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('게시글 수정 실패:', error);
      alert('게시글 수정에 실패했습니다.');
    }
  };

  return (
    <div className="write-post-container">
      <h2>게시글 수정</h2>
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
          <button type="submit">수정하기</button>
          <button 
            type="button" 
            onClick={() => navigate(`/community/post/${postId}`)}
            className="cancel-button"
          >
            취소
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditPost; 