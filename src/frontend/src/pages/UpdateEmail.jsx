import { Link } from "react-router-dom";

function UpdateEmail() {
    return (
        <div className="update-page">
            <div className="update-card">
                <h1 className="update-h1">Update Email</h1>
                <p className="subtitle">Update your email address.</p>

                <form className="update-form">
                    <label>
                        Current Email
                        <input type="text" placeholder="Enter your current email" required />
                    </label>

                    <label>
                        New Email
                        <input type="text" placeholder="Enter your new email" required />
                    </label>

                    <label>
                        Password
                        <input type="password" placeholder="Enter your password" required />
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

export default UpdateEmail;