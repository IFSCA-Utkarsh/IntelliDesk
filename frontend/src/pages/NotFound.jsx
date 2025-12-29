import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="not-found">
      <h1>Page Not Found</h1>
      <p>The page you are trying to access does not exist.</p>
      <Link to="/chatbot">Go to Dashboard</Link>
    </div>
  );
}
