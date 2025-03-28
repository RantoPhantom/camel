import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import RootLayout from './layout/RootLayout';
import reportWebVitals from './reportWebVitals';
import {
  createBrowserRouter,
  createRoutesFromElements,
  Navigate,
  Route,
  RouterProvider
} from 'react-router-dom'
import NewChat from './page/NewChat';
import ChatDetail from './page/ChatDetail';
import Login from './page/Login';
import SignUp from './page/SignUp';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/">
      <Route index element={<Navigate to={"./chat"} />} />
      <Route path="login" element={<Login />} />
      <Route path="signup" element={<SignUp />} />
      <Route path="chat" element={<RootLayout />}>
        <Route index element={<Navigate to={"./newchat"} />} />
        <Route path="newchat" element={<NewChat />} />
        <Route path="chatdetail" element={<ChatDetail />} />
      </Route>
    </Route>
  )
)



const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
