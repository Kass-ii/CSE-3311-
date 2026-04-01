import { Link, useNavigate } from "react-router-dom";

function Settings(){
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem("token");

        navigate("/");
    };

    return(
        <div className="settings-page">
            <div className="settings-card">
                <h1 className="settings-h1">Settings</h1>
                <div className="settings-grid">

                    <Link to="/Profile" className="settings-btn">Profile</Link>

                    <Link to="/Account" className="settings-btn">Account</Link>

                    <button className="settings-btn" onClick={handleLogout}>Log Out</button>

                </div>
            </div>
        </div>
    );
} 

export default Settings;