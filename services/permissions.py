from models import models


class UserPermissions:
    @staticmethod
    def admin_access(user: models.User) -> bool:
        return user.role != 'admin'

    @staticmethod
    def admin_or_moderator_access(user: models.User) -> bool:
        return not user.role in ('admin', 'moderator')

    @staticmethod
    def admin_or_moderator_or_self_access(
        user: models.User, author: models.User
    ):
        if author.username != user.username:
            return True
        return not user.role in ('admin', 'moderator')
