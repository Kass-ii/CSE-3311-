import { Link } from "react-router-dom";

function MainMenu() {
    return (
        <div className="menu-page">
            <div className="menu-card">
                <h1>Main Menu</h1>
                <p className="subtitle">Choose where you want to go next.</p>

                <div className="menu-options">
                    <Link to="/planner" className="menu-button">
                        Open Planner
                    </Link>

                    <Link to="/map" className="menu-button secondary">
                        Open Map
                    </Link>

                    <button className="menu-button secondary">
                        Account Settings
                    </button>
                </div>
            </div>
        </div>
    );
}

export default MainMenu;