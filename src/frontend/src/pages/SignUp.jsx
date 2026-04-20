// @jsx h
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { registerUser } from "../api/auth";

function SignUp() {
    const navigate = useNavigate();

    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");

    const handleSignUp = async (e) => {
        e.preventDefault();
        setError("");

        try {
            await registerUser(email, password, confirmPassword);
            window.location.href = "/menu";
        } catch (err) {
            setError(err.message);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <h1>Create Account</h1>
                <p className="subtitle">Sign up to start using ComfortRoute.</p>

                <form onSubmit={handleSignUp} className="auth-form">
                    <label>
                        Full Name
                        <input
                            type="text"
                            placeholder="Enter your full name"
                            required
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                        />
                    </label>

                    <label>
                        Email
                        <input
                            type="email"
                            placeholder="Enter your email"
                            required
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </label>

                    <label>
                        Password
                        <input
                            type="password"
                            placeholder="Create a password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </label>

                    <label>
                        Confirm Password
                        <input
                            type="password"
                            placeholder="Confirm your password"
                            required
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    </label>

                    {error && <p style={{ color: "red" }}>{error}</p>}

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