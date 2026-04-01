import { Link, useNavigate } from "react-router-dom";

function Settings(){
    const navigate = useNavigate();

    return(
        <div className="settings-page">
            <div className="settings-card">
                <h1>Settings</h1>
                <div className="settings-grid">
                    <button id="profile" className="settings-btn">Profile</button><br></br>
                    <button id="account-settings" className="settings-btn">Account Settings</button><br></br>
                    <button id="notifications" className="settings-btn">Notifications</button><br></br>
                    <button id="log out" className="settings-btn">Log Out</button><br></br>
                </div>
            </div>
        </div>
    );
} 

export default Settings;