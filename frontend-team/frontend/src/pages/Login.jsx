import { Link, useNavigate } from "react-router-dom";

function Login() {
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // For now, this just sends the user to the main menu
    navigate("/menu");
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>ComfortRoute</h1>
        <p className="subtitle">Log in to access your transit planner.</p>

        <form onSubmit={handleLogin} className="auth-form">
          <label>
            Email
            <input type="email" placeholder="Enter your email" required />
          </label>

          <label>
            Password
            <input type="password" placeholder="Enter your password" required />
          </label>

          <button type="submit">Log In</button>
        </form>

        <div className="auth-links">
          <Link to="/forgot-password">Forgot Password?</Link>
          <p>
            Don�t have an account? <Link to="/signup">Sign Up</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
