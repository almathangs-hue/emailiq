import { Routes, Route, Navigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import Login from "@/pages/Login";
import Dashboard from "@/pages/Dashboard";
import ApplicationDetail from "@/pages/ApplicationDetail";

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token);
  return token ? <>{children}</> : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Dashboard />
          </PrivateRoute>
        }
      />
      <Route
        path="/applications/:id"
        element={
          <PrivateRoute>
            <ApplicationDetail />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
