import { lazy } from 'react'

// Lazy load pages to enable code splitting
const Home = lazy(() => import('@/pages/Home'))
const Results = lazy(() => import('@/pages/Results'))
const Chat = lazy(() => import('@/pages/Chat'))
const About = lazy(() => import('@/pages/About'))
const Research = lazy(() => import('@/pages/Research'))
const NotFound = lazy(() => import('@/pages/NotFound'))

export const routes = [
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/results',
    element: <Results />,
  },
  {
    path: '/chat',
    element: <Chat />,
  },
  {
    path: '/about',
    element: <About />,
  },
  {
    path: '/research',
    element: <Research />,
  },
  {
    path: '*',
    element: <NotFound />,
  },
]