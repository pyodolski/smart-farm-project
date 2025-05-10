import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './PostDetail.css';

function PostDetail() {
  const [post, setPost] = useState(null);
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [likeCount, setLikeCount] = useState(0);
  const { postId } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPostDetail();
  }, [postId]);

  const fetchPostDetail = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/posts/${postId}`, {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setPost(data.post);
        setComments(data.comments);
        setLikeCount(data.like_count);
      }
    } catch (error) {
      console.error('게시글 로딩 실패:', error);
    }
  };

  const handleLike = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/posts/${postId}/like`, {
        method: 'POST',
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setLikeCount(data.like_count);
      }
    } catch (error) {
      console.error('좋아요 실패:', error);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('정말 삭제하시겠습니까?')) {
      try {
        const response = await fetch(`http://localhost:5001/api/posts/${postId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.ok) {
          navigate('/community');
        }
      } catch (error) {
        console.error('게시글 삭제 실패:', error);
      }
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://localhost:5001/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ content: newComment })
      });
      if (response.ok) {
        setNewComment('');
        fetchPostDetail();
      }
    } catch (error) {
      console.error('댓글 작성 실패:', error);
    }
  };

  const handleCommentDelete = async (commentId) => {
    if (window.confirm('댓글을 삭제하시겠습니까?')) {
      try {
        const response = await fetch(`http://localhost:5001/api/comments/${commentId}`, {
          method: 'DELETE',
          credentials: 'include'
        });
        if (response.ok) {
          fetchPostDetail();
        }
      } catch (error) {
        console.error('댓글 삭제 실패:', error);
      }
    }
  };

  if (!post) return <div>로딩 중...</div>;

  return (
    <div className="post-detail-container">
      <div className="post-header">
        <h2>{post.title}</h2>
        <div className="post-info">
          <span>작성자: {post.name}</span>
          <span>작성일: {new Date(post.wdate).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="post-content">
        <pre>{post.content}</pre>
      </div>

      <div className="post-actions">
        <button onClick={handleLike}>❤️ 좋아요 ({likeCount})</button>
        {post.is_author && (
          <>
            <button onClick={() => navigate(`/community/edit/${postId}`)}>
              ✏️ 수정
            </button>
            <button onClick={handleDelete}>🗑️ 삭제</button>
          </>
        )}
      </div>

      <div className="comments-section">
        <h3>💬 댓글</h3>
        <form onSubmit={handleCommentSubmit}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="댓글을 입력하세요"
            required
          />
          <button type="submit">댓글 작성</button>
        </form>

        <div className="comments-list">
          {comments.map(comment => (
            <div key={comment.id} className="comment">
              <div className="comment-header">
                <strong>{comment.commenter}</strong>
                <span>{new Date(comment.cdate).toLocaleDateString()}</span>
              </div>
              <p>{comment.content}</p>
              {comment.is_author && (
                <div className="comment-actions">
                  <button onClick={() => navigate(`/community/comment/edit/${comment.id}`)}>
                    ✏️ 수정
                  </button>
                  <button onClick={() => handleCommentDelete(comment.id)}>
                    🗑️ 삭제
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <button 
        className="back-button"
        onClick={() => navigate('/community')}
      >
        ← 목록으로
      </button>
    </div>
  );
}

export default PostDetail; 