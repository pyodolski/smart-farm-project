import React, { useState, useEffect, useContext } from 'react';
import {BrowserRouter as Router, Route, Routes, Navigate, useNavigate} from 'react-router-dom';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import MainPage from './pages/main/MainPage';
import UserProfile from './pages/user/UserProfile';
import Community from './pages/community/Board';
import PostDetail from './pages/community/PostDetail';
import WritePost from './pages/community/WritePost';
import EditPost from './pages/community/EditPost';
import EditComment from './pages/community/EditComment';
import Encyclopedia from './pages/encyclopedia/Encyclopedia';
import EncyclopediaDetail from './pages/encyclopedia/EncyclopediaDetail';
import DiseaseDetail from './pages/encyclopedia/DiseaseDetail';
import InsectDetail from './pages/encyclopedia/InsectDetail';
import EnemyDetail from './pages/encyclopedia/EnemyDetail';
import Products from './pages/products/Products';
import Statistics from './pages/statistics/Statistics';
import './App.css';
import logo from './image/leaves-growing-from-ground-green-glyph-style_78370-6720.png';
import { AuthContext } from './contexts/AuthContext';
import CameraSetting from './pages/camera/CameraSetting';
import FarmDetail from './pages/farm/FarmDetail';
import API_BASE_URL from './utils/config';
import GreenhouseGrid from './pages/greenhouse/GreenhouseGrid';
import Navbar from './components/common/Navbar';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

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
      } finally {
        setIsLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#f7f7f7'
      }}>
        <div style={{
          textAlign: 'center',
          color: '#666'
        }}>
          <div>로딩 중...</div>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={[isLoggedIn, setIsLoggedIn]}>
      <div className="app-root">
        <Router>
          <Navbar />
          <div className="app-content">
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
              <Route path="/iot-setting" element={isLoggedIn ? <CameraSetting /> : <Navigate to="/login" />} />
              <Route path="/iot-setting/:deviceId" element={isLoggedIn ? <CameraSetting /> : <Navigate to="/login" />} />
              <Route path="/farm/:farmId" element={isLoggedIn ? <FarmDetail /> : <Navigate to="/login" />} />
              <Route path="/farm-detail/:farmId" element={isLoggedIn ? <FarmDetail /> : <Navigate to="/login" />} />
              <Route path="/greenhouse-grid/:farmId" element={isLoggedIn ? <GreenhouseGrid /> : <Navigate to="/login" />} />
            </Routes>
          </div>
        </Router>
      </div>
    </AuthContext.Provider>
  );
}

export default App;
