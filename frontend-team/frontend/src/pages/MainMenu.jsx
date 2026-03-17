import { Link } from "react-router-dom";

function MainMenu() {
    return (
        <div className="menu-page">
            <div className="menu-card">

                <h1>ComfortRoute</h1>
                <h2>Main Menu</h2>

                <p className="menu-subtitle">
                    Choose where you want to go next.
                </p>

                <div className="menu-grid">

                    <Link to="/planner" className="menu-button">
                        🚆 Open Planner
                    </Link>

                    <Link to="/map" className="menu-button">
                        🗺️ Open Map
                    </Link>

                    <button className="menu-button secondary">
                        ⚙️ Account Settings
                    </button>

                </div>

            </div>
        </div>
    );
}

export default MainMenu;