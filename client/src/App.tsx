import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import Home from './routes/Home';
import Login from './routes/Login';
import Register from './routes/Register';
import Admin_Users from './routes/Admin-Users';
import Admin_Feeds from './routes/Admin-Feeds';
import About from './routes/About';

const App = () => {
    return (
        <BrowserRouter>
            <Navigation />
            <Routes>
                <Route path="/" element={<Navigate to="/home" replace />} />
                <Route path="/home" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/about" element={<About />} />
                <Route path="/admin/users" element={<Admin_Users />} />
                <Route path="/admin/feeds" element={<Admin_Feeds />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
