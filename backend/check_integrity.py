
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.masters.models import Master, MasterShift
from apps.accounts.models import User
from apps.clients.models import Client

def check_data():
    print("Checking Masters...")
    masters = Master.objects.all()
    for m in masters:
        print(f"Master ID: {m.id}, User: {m.user.username if m.user else 'NONE'}, Org: {m.organization.id if m.organization else 'NONE'}, Names: {m.user.first_name if m.user else ''} {m.user.last_name if m.user else ''}")
        if not m.user:
            print(f"!!! Master {m.id} has no User object")
        if not m.organization:
            print(f"!!! Master {m.id} has no Organization")
        if m.user and m.user.organization != m.organization:
            print(f"!!! Master {m.id} organization ({m.organization.id}) differs from User organization ({m.user.organization.id})")

    print("\nChecking Clients...")
    clients = Client.objects.all()
    for c in clients:
        print(f"Client ID: {c.id}, Phone: {c.phone}, Org: {c.organization.id if c.organization else 'NONE'}, User: {c.user.username if c.user else 'NONE'}")
        if not c.organization:
            print(f"!!! Client {c.id} has no Organization")
            
    print("\nChecking Users...")
    users = User.objects.all()
    for u in users:
        print(f"User ID: {u.id}, Username: {u.username}, Role: {u.role}, Org: {u.organization.id if u.organization else 'NONE'}")

if __name__ == "__main__":
    check_data()
