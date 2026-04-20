import { Link } from "react-router-dom";
import { logoutUser } from "../api/auth";

function AccountSettings() {
    const handleLogout = async () => {
        try {
            await logoutUser();
            window.location.href = "/";
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="account-page">
            <div className="account-card">
                <h1 className="account-h1">Account Settings</h1>

                <div className="account-grid">
                    <Link to="/update-email" className="account-btn">
                        📧 Update Email
                    </Link>

                    <Link to="/update-password" className="account-btn">
                        🔒 Update Password
                    </Link>

                    <Link to="/settings" className="account-btn">
                        ⚙️ App Preferences
                    </Link>

                    <button className="account-btn" onClick={handleLogout}>
                        ↪ Log Out
                    </button>
                </div>
            </div>
        </div>
    );
}

export default AccountSettings;
