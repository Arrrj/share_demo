from rest_framework.permissions import BasePermission

class IsRecruiter(BasePermission):
    message = None

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.user_role == 'recruiter':
            return True
        self.message = "You must be a recruiter to access this resource."
        return False