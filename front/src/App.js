import React, { useState, useEffect, useContext } from 'react';
import {BrowserRouter as Router, Route, Routes, Navigate, useNavigate} from 'react-router-dom';
import Login from './Login';
import Register from './Register';
import MainPage from './MainPage';
import UserProfile from './UserProfile';
import Community from './Community';
import PostDetail from './PostDetail';
import WritePost from './WritePost';
import EditPost from './EditPost';
import EditComment from './EditComment';
import Encyclopedia from './Encyclopedia';
import EncyclopediaDetail from './EncyclopediaDetail';
import DiseaseDetail from './DiseaseDetail';
import InsectDetail from './InsectDetail';
import EnemyDetail from './EnemyDetail';
import Products from './Products';
import Statistics from './Statistics';
import './App.css';
import logo from './leaves-growing-from-ground-green-glyph-style_78370-6720.png'
import { AuthContext } from './contexts/AuthContext';
import CameraSetting from './CameraSetting';
import FarmDetail from './FarmDetail';
import API_BASE_URL from './config';

function Navigation() {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useContext(AuthContext);

  const handleLogoClick =() =>{
    navigate('/');
  };

  const handleLogout = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/logout`, {
        method: 'POST',
        credentials: 'include'
      });

      if (response.ok) {
        sessionStorage.removeItem('isLoggedIn');
        sessionStorage.removeItem('userId');
        setIsLoggedIn(false);
        navigate('/login');
      }
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  return(
    <nav className="navbar">
      <div className="nav-brand" onClick={handleLogoClick}>
        <img 
          src={logo}
          alt="Smart Farm Hub" 
          className="nav-logo" 
        />
        <span className="brand-text" style={{fontSize: "1.6rem"}}>Smart Farm Hub</span>
      </div>
      <div className="nav-menu">
        {isLoggedIn &&(
          <div className="menu-items">
            <a onClick={()=> navigate('/Products')}>Products</a>
            <a onClick={()=> navigate('/encyclopedia')}>Encyclopedia</a>
            <a onClick={()=> navigate('/')}>Farm</a>
            <a onClick={()=> navigate('/Statistics')}>Statistics</a>
            <a onClick={()=> navigate('/community')}>Community</a>
          </div>
        )}
        {isLoggedIn &&(
          <>
            <button
              className="login-btn" 
              onClick={()=> navigate('/profile')}
            >
              {sessionStorage.getItem('userId')}님 환영합니다
            </button>
            <button 
              className="logout-btn" 
              onClick={handleLogout}
            >
              로그아웃
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/check_login`, {
          credentials: 'include'
        });
        const data = await response.json();
        
        if (data.logged_in) {
          setIsLoggedIn(true);
          sessionStorage.setItem('isLoggedIn', 'true');
          sessionStorage.setItem('userId', data.user_id);
        } else {
          setIsLoggedIn(false);
          sessionStorage.removeItem('isLoggedIn');
          sessionStorage.removeItem('userId');
        }
      } catch (error) {
        console.error('로그인 상태 확인 실패:', error);
        setIsLoggedIn(false);
        sessionStorage.removeItem('isLoggedIn');
        sessionStorage.removeItem('userId');
      }
    };

    checkLoginStatus();
  }, []);

  return (
    <AuthContext.Provider value={[isLoggedIn, setIsLoggedIn]}>
      <Router>
        <div className="app-container">
          <Navigation />
          <Routes>
            <Route path="/" element={isLoggedIn ? <MainPage /> : <Navigate to="/login" />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/profile" element={isLoggedIn ? <UserProfile /> : <Navigate to="/login" />} />
            <Route path="/community" element={isLoggedIn ? <Community /> : <Navigate to="/login" />} />
            <Route path="/Products" element={isLoggedIn ? <Products /> : <Navigate to="/login" />} />
            <Route path="/community/write" element={isLoggedIn ? <WritePost /> : <Navigate to="/login" />} />
            <Route path="/community/post/:postId" element={isLoggedIn ? <PostDetail /> : <Navigate to="/login" />} />
            <Route path="/community/edit/:postId" element={isLoggedIn ? <EditPost /> : <Navigate to="/login" />} />
            <Route path="/community/comment/edit/:commentId" element={isLoggedIn ? <EditComment /> : <Navigate to="/login" />} />
            <Route path="/encyclopedia" element={isLoggedIn ? <Encyclopedia /> : <Navigate to="/login" />} />
            <Route path="/encyclopedia/:crop" element={isLoggedIn ? <EncyclopediaDetail /> : <Navigate to="/login" />} />
            <Route path="/encyclopedia/disease/:diseaseId" element={isLoggedIn ? <DiseaseDetail /> : <Navigate to="/login" />} />
            <Route path="/encyclopedia/insect/:insectId" element={isLoggedIn ? <InsectDetail /> : <Navigate to="/login" />} />
            <Route path="/encyclopedia/enemy/:enemyId" element={isLoggedIn ? <EnemyDetail /> : <Navigate to="/login" />} />
            <Route path="/statistics" element={isLoggedIn ? <Statistics /> : <Navigate to="/login" />} />
            <Route path="/iot-setting" element={<CameraSetting />} />
            <Route path="/farm-card-tail/:farmId" element={isLoggedIn ? <FarmDetail /> : <Navigate to="/login" />} />
          </Routes>
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;
