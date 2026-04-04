import { Link, useNavigate } from "react-router-dom";

function Account(){

    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");

        navigate("/");
    };

    return(
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

                    <button className="account-btn" onClick={handleLogout}>↪ Log Out</button>
                </div>

            </div>
        </div>
    );
};

export default Account;