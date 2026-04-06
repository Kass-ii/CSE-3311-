import { Link } from "react-router-dom";

function UpdatePassword() {
    return (
        <div className="update-page">
            <div className="update-card">
                <h1 className="update-h1">Update Password</h1>
                <p className="subtitle">Update your password.</p>

                <form className="update-form">
                    <label>
                        Current Password
                        <input type="password" placeholder="Enter your current password" required />
                    </label>

                    <label>
                        New Password
                        <input type="password" placeholder="Enter your new password" required />
                    </label>

                    <label>
                        Confirm Password
                        <input type="password" placeholder="Re-enter your new password" required />
                    </label>

                    <button type="submit">Submit</button>
                </form>

                <Link to="/account-settings" className="menu-button back-main-center">
                    ← Back to Account Settings
                </Link>
            </div>
        </div>
    );
}

export default UpdatePassword;