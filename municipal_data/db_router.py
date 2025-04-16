# db_router.py (project root or inside an app directory)
class RegionDatabaseRouter:
    """
    A database router to direct queries to the appropriate regional database.
    """

    def db_for_read(self, model, **hints):
        request = hints.get('request')
        if request and hasattr(request.user, 'region'):
            return request.user.region.db_name  # `db_name` is a field storing the database name for the region
        return 'default'

    def db_for_write(self, model, **hints):
        request = hints.get('request')
        if request and hasattr(request.user, 'region'):
            return request.user.region.db_name
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {obj1._state.db, obj2._state.db}
        return len(db_set) == 1

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
