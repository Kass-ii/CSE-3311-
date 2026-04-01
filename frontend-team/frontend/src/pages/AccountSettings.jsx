import { Link, useNavigate } from "react-router-dom";

function AccountSettings(){
    const navigate = useNavigate();

    return(
        <div className="settings-page">
            <div className="settings-card">
                <h1>Account Settings</h1>

            </div>
        </div>
    );
} 

export default AccountSettings;