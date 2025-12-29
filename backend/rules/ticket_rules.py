from collections import defaultdict

def assign_admin(tickets, admins):
    counts = defaultdict(int)
    for t in tickets:
        if t.get("assigned_admin"):
            counts[t["assigned_admin"]] += 1

    admins_sorted = sorted(admins, key=lambda a: counts[a["id"]])
    return admins_sorted[0]["id"] if admins_sorted else None
