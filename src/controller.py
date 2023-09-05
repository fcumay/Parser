from fastapi import HTTPException


class ExceptionMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            await self.app(scope, receive, send)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail="Server error")
