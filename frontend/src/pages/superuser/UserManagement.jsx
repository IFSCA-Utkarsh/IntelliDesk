import RequireRole from "../../components/RequireRole";
import { ROLES } from "../../constants/roles";

export default function UserManagement() {
  return (
    <RequireRole allowed={[ROLES.SUPERUSER]}>
      <section>
        <h1>User Management</h1>
        <p className="muted">Suspend / Unsuspend users</p>
      </section>
    </RequireRole>
  );
}
