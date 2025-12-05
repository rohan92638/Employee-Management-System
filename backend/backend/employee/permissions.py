from rest_framework import permissions

class IsAdminOrManagerOrSelf(permissions.BasePermission):
    """
    Admin (is_staff) — full access.
    Manager (in group 'Manager') — can view employees in their department and manage some things.
    Employee user — can view/edit their own Employee record.
    """

    def has_permission(self, request, view):
        # Must be authenticated for all employee endpoints except maybe list (depending on your policy)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin -> full
        if getattr(user, 'is_staff', False):
            return True

        # If user has 'Manager' group
        if user.groups.filter(name='Manager').exists():
            # Allow if manager and employee is in same department
            employee_department = getattr(obj, 'department', None)
            # If manager has Employee instance and department, allow within same department
            try:
                manager_employee = user.employee
            except Exception:
                manager_employee = None

            if manager_employee and employee_department and manager_employee.department == employee_department:
                # allow read and maybe write for manager; tune as needed
                if request.method in permissions.SAFE_METHODS or request.method in ('PUT', 'PATCH'):
                    return True

        # If the employee object is linked to user -> allow self
        try:
            if obj.user and obj.user == user:
                # allow view and edit own data
                return True
        except Exception:
            pass

        return False
