import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

function EditComment() {
  const [content, setContent] = useState('');
  const [postId, setPostId] = useState(null);
  const { commentId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchComment();
  }, [commentId]);

  const fetchComment = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/comments/${commentId}`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setContent(data.content);
        setPostId(data.post_id);
      } else {
        navigate('/community');
      }
    } catch (error) {
      console.error('댓글 로딩 실패:', error);
      navigate('/community');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch(`http://localhost:5000/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ content })
      });

      if (response.ok) {
        navigate(`/community/post/${postId}`);
      } else {
        const data = await response.json();
        alert(data.message || '댓글 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('댓글 수정 실패:', error);
      alert('댓글 수정에 실패했습니다.');
    }
  };

  return (
    <div className="write-post-container">
      <h2>댓글 수정</h2>
      <form onSubmit={handleSubmit}>
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

export default EditComment; 