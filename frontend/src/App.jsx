import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import SignUp from "./components/Signup"; 
import SignIn from "./components/Signin"; 
import Home from "./components/Home";
import "@progress/kendo-theme-default/dist/all.css"; 

function App() {
  return (
      <div style={{ textAlign: "center", padding: "20px" }}>
        <h1>Welcome to the App</h1>
        <Routes>
          {/* Default Route - Redirect to SignUp */}
          <Route path="/" element={<Navigate to="/signup" />} />
          {/* SignUp Route */}
          <Route path="/signup" element={<SignUp />} />
          {/* SignIn Route */}
          <Route path="/signin" element={<SignIn />} />
          {/* Home Route */}
          <Route path="/home" element={<Home /> } />
        </Routes>
      </div>
  );
}

export default App;
