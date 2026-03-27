// @jsx h
import { Link, useNavigate } from "react-router-dom";

function SignUp() {
    const navigate = useNavigate();

    const handleSignUp = (e) => {
        e.preventDefault();

        // For now, just move to the main menu
        navigate("/menu");
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Create Account</h1>
                <p className="subtitle">Sign up to start using ComfortRoute.</p>

                <form onSubmit={handleSignUp} className="auth-form">
                    <label>
                        Full Name
                        <input type="text" placeholder="Enter your full name" required />
                    </label>

                    <label>
                        Email
                        <input type="email" placeholder="Enter your email" required />
                    </label>

                    <label>
                        Password
                        <input type="password" placeholder="Create a password" required />
                    </label>

                    <label>
                        Confirm Password
                        <input type="password" placeholder="Confirm your password" required />
                    </label>

                    <button type="submit">Create Account</button>
                </form>

                <div className="auth-links">
                    <p>
                        Already have an account? <Link to="/">Log In</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default SignUp;