import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Topics from "./pages/Topics.jsx";
import Lesson from "./pages/Lesson.jsx";
import Quiz from "./pages/Quiz.jsx";
import Progress from "./pages/Progress.jsx";
import Achievements from "./pages/Achievements.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/"                              element={<Home />} />
          <Route path="/topics"                        element={<Topics />} />
          <Route path="/lesson/:subject/:topic"        element={<Lesson />} />
          <Route path="/quiz/:subject"                 element={<Quiz />} />
          <Route path="/quiz/:subject/:topic"          element={<Quiz />} />
          <Route path="/progress"                      element={<Progress />} />
          <Route path="/achievements"                  element={<Achievements />} />
          <Route path="*"                              element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
