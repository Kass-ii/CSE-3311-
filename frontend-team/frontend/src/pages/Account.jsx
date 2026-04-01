function Account(){
    return(
        <div className="account-page">
            <div className="account-card">
                <h1 className="account-h1">Account</h1>

                <div className="account-grid">
                    <button className="account-btn">Update Email</button>
                    <button className="account-btn">Update Password</button>
                    <button className="account-btn">Filler</button>
                </div>

            </div>
        </div>
    );
};

export default Account;