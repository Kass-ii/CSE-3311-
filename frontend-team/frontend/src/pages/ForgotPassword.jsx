import { Link } from "react-router-dom";

function ForgotPassword() {
    const handleReset = (e) => {
        e.preventDefault();
        alert("Password reset link sent to your email.");
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Forgot Password</h1>
                <p className="subtitle">Enter your email to receive a reset link.</p>

                <form onSubmit={handleReset} className="auth-form">
                    <label>
                        Email
                        <input type="email" placeholder="Enter your email" required />
                    </label>

                    <button type="submit">Send Reset Link</button>
                </form>

                <div className="auth-links">
                    <p>
                        Back to <Link to="/">Log In</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default ForgotPassword;