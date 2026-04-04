function UpdateEmail(){
    return(
        <div className="update-page">
            <div className="update-card">
                <h1 className="update-h1">Update Email</h1>
                <p className="subtitle">Update your email address.</p>

                <form className="update-form">
                    <label>
                       Current Email
                       <input type="text" placeholder="Enter your current email" required></input>
                    </label>

                    <label>
                        New Email
                        <input type="text" placeholder="Enter your new email" required></input>
                    </label>

                    <label>
                        Password
                       <input type="text" placeholder="Enter your password" required></input>
                    </label>

                    <button type="submit">Submit</button>
                </form>

                
            </div>
        </div>

    );
}

export default UpdateEmail;