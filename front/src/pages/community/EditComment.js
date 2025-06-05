import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import API_BASE_URL from '../../utils/config';

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
      const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setContent(data.content);
        setPostId(data.board_id);
        
        if (!data.board_id) {
          console.error('게시글 ID를 찾을 수 없습니다.');
          navigate('/community');
          return;
        }
      } else {
        const errorData = await response.json();
        alert(errorData.message || '댓글을 불러올 수 없습니다.');
        navigate('/community');
      }
    } catch (error) {
      console.error('댓글 로딩 실패:', error);
      alert('댓글을 불러오는 중 오류가 발생했습니다.');
      navigate('/community');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!postId) {
      alert('게시글 정보를 찾을 수 없습니다.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          content,
          board_id: postId
        })
      });

      if (response.ok) {
        navigate(`/community/post/${postId}`);
      } else {
        const errorData = await response.json();
        alert(errorData.message || '댓글 수정에 실패했습니다.');
      }
    } catch (error) {
      console.error('댓글 수정 실패:', error);
      alert('댓글 수정 중 오류가 발생했습니다.');
    }
  };

  if (!postId) {
    return <div>로딩 중...</div>;
  }

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