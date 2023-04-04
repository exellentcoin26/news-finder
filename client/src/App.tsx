import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import Navigation from './components/Navigation';
import Home from './routes/Home';
import Login from './routes/Login';
import Register from './routes/Register';
import Admin from './routes/Admin';
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
                <Route path="/admin" element={<Admin />} />
                <Route path="/about" element={<About />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
