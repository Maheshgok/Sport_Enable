/**
 * Protected Route Component
 * Wraps routes that require authentication
 */

import { Navigate } from 'react-router-dom';
import { getAuthToken, getAuthUser } from './Login';

/**
 * ProtectedRoute - Requires user to be logged in
 */
export function ProtectedRoute({ children }) {
  const token = getAuthToken();
  
  if (!token) {
    // Redirect to login if not authenticated
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

/**
 * RoleProtectedRoute - Requires specific role(s)
 */
export function RoleProtectedRoute({ children, allowedRoles = [] }) {
  const token = getAuthToken();
  const user = getAuthUser();
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  // Check if user has any of the allowed roles
  const hasPermission = allowedRoles.length === 0 || 
    user?.roles?.some(role => allowedRoles.includes(role));
  
  if (!hasPermission) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return children;
}

/**
 * Example usage in App.jsx or routes file:
 * 
 * import { BrowserRouter, Routes, Route } from 'react-router-dom';
 * import { ProtectedRoute, RoleProtectedRoute } from './components/auth/ProtectedRoute';
 * import Login from './components/auth/Login';
 * import Dashboard from './pages/Dashboard';
 * import AdminPanel from './pages/AdminPanel';
 * 
 * function App() {
 *   return (
 *     <BrowserRouter>
 *       <Routes>
 *         <Route path="/login" element={<Login />} />
 *         
 *         <Route path="/dashboard" element={
 *           <ProtectedRoute>
 *             <Dashboard />
 *           </ProtectedRoute>
 *         } />
 *         
 *         <Route path="/admin" element={
 *           <RoleProtectedRoute allowedRoles={['admin', 'super_user']}>
 *             <AdminPanel />
 *           </RoleProtectedRoute>
 *         } />
 *       </Routes>
 *     </BrowserRouter>
 *   );
 * }
 */

/**
 * AdminOnly - Show content only for admin users
 */
export function AdminOnly({ children }) {
  const user = getAuthUser();
  const isAdmin = user?.roles?.some(role => 
    role === 'admin' || role === 'super_user'
  );
  
  if (!isAdmin) {
    return null;
  }
  
  return children;
}

/**
 * RoleBasedContent - Render different content based on role
 */
export function RoleBasedContent({ role, children }) {
  const user = getAuthUser();
  const hasRole = user?.roles?.includes(role);
  
  if (!hasRole) {
    return null;
  }
  
  return children;
}

/**
 * Example usage:
 * 
 * <AdminOnly>
 *   <button onClick={handleDelete}>Delete User</button>
 * </AdminOnly>
 * 
 * <RoleBasedContent role="athlete">
 *   <AthleteDashboard />
 * </RoleBasedContent>
 * 
 * <RoleBasedContent role="physiotherapist">
 *   <PhysioPanel />
 * </RoleBasedContent>
 */
