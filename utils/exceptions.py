


class AppError(Exception):
    pass

class BusinessRuleError(AppError):
    pass

class ValidationError(AppError):
    pass

class NotFoundError(AppError):
    pass
