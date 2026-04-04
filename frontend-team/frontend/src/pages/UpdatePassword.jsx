function UpdatePassword(){

    return(
        <div className="update-page">
            <div className="update-card">
                <h1 className="update-h1">Update Password</h1>
                <p className="subtitle">Update your password.</p>

                <form className="update-form">
                    <label>
                       Current Password 
                       <input type="text" placeholder="Enter your current password" required></input>
                    </label>

                    <label>
                        New Password
                        <input type="text" placeholder="Enter your new password" required></input>
                    </label>

                    <label>
                        Confirm Password
                       <input type="text" placeholder="Re-enter your new password" required></input>
                    </label>

                    <button type="submit">Submit</button>
                </form>

                
            </div>
        </div>

    );

};

export default UpdatePassword;