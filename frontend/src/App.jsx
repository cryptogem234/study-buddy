import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Topics from './pages/Topics'
import Lesson from './pages/Lesson'
import Quiz from './pages/Quiz'
import Progress from './pages/Progress'
import Vocabulary from './pages/Vocabulary'
import Reading from './pages/Reading'
import ReadingPassage from './pages/ReadingPassage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/subjects/:subjectId" element={<Topics />} />
          <Route path="/topics/:topicId/lesson" element={<Lesson />} />
          <Route path="/topics/:topicId/quiz" element={<Quiz />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/topics/:topicId/vocabulary" element={<Vocabulary />} />
          <Route path="/reading" element={<Reading />} />
          <Route path="/reading/:passageId" element={<ReadingPassage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
